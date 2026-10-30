#include "docgraph.h"
#include "ui_docgraph.h"

#include <QScreen>
#include <QSqlQuery>
#include <QSqlError>
#include <QMessageBox>
#include <QGraphicsTextItem>
#include <QDebug>

docGraph::docGraph(QWidget *parent) :
    QDialog(parent),
    ui(new Ui::docGraph)
{
    ui->setupUi(this);

    // set window flags
    setWindowFlag(Qt::FramelessWindowHint);
    setAttribute(Qt::WA_TranslucentBackground, true);

    // Center the window on the screen using QScreen
    QScreen *screen = QGuiApplication::primaryScreen();
    QRect screenGeometry = screen->geometry();
    int x = (screenGeometry.width() - this->width()) / 2;
    int y = (screenGeometry.height() - this->height()) / 2;
    this->move(x, y);

    // Initialize database connection
    db = QSqlDatabase::addDatabase("QSQLITE");
    db.setDatabaseName("icure_demo.sqlite");
    if (!db.open()) {
        QMessageBox::critical(this, "Error", "Could not open database");
        return;
    }

    // Initialize graphics scene
    scene = new QGraphicsScene(this);
    ui->graphicsView->setScene(scene);

    // Initialize pie chart
    pieChart = new QChart();
    chartView = new QChartView(pieChart);
    chartView->setRenderHint(QPainter::Antialiasing);

    ui->verticalLayout->addWidget(chartView);
    chartView->hide();

    loadDocClasses();
    showPatientDistribution();
    createDocClassPieChart();
}

docGraph::~docGraph()
{
    delete ui;
    delete pieChart;
    delete chartView;
}

void docGraph::on_backBtn_clicked()
{
    this->close();
}

void docGraph::on_classListWidget_itemClicked(QListWidgetItem *item)
{
    QString docClass = item->text();
    showSymptomGraph(docClass);
    toggleChartView(false);
}

void docGraph::on_showPieChartBtn_clicked()
{
    toggleChartView(true);  // Show the pie chart view
}

void docGraph::toggleChartView(bool showPieChart)
{
    if (showPieChart) {
        ui->graphicsView->hide();
        chartView->show();
        ui->showPieChartBtn->setText("Show Symptom Graph");
    } else {
        chartView->hide();
        ui->graphicsView->show();
        ui->showPieChartBtn->setText("Show Doc Class Distribution");
    }
}

void docGraph::loadDocClasses()
{
    QSqlQuery query;
    if (query.exec("SELECT DISTINCT doc_class FROM DocPat_Relation")) {
        while (query.next()) {
            QString docClass = query.value(0).toString();
            ui->classListWidget->addItem(docClass);
        }
    } else {
        QMessageBox::critical(this, "Error", "Failed to load doc classes: " + query.lastError().text());
    }
}

void docGraph::showSymptomGraph(const QString &docClass)
{
    scene->clear();

    QSqlQuery query;
    query.prepare("SELECT symptoms, COUNT(*) as count FROM DocPat_Relation WHERE doc_class = :docClass GROUP BY symptoms");
    query.bindValue(":docClass", docClass);

    if (query.exec()) {
        int yPos = 0;
        while (query.next()) {
            QString symptom = query.value("symptoms").toString();
            int count = query.value("count").toInt();

            QGraphicsRectItem *bar = new QGraphicsRectItem(0, yPos, count * 10, 20);
            bar->setBrush(QBrush(Qt::blue));
            scene->addItem(bar);

            QGraphicsTextItem *label = scene->addText(symptom + ": " + QString::number(count));
            label->setPos(-100, yPos);

            yPos += 30;
        }

        if (yPos == 0) {
                QGraphicsTextItem *noDataText = scene->addText("No data available for this doc_class");
                noDataText->setPos(0, 0);
            }
        } else {
            QMessageBox::critical(this, "Error", "Failed to fetch symptom data: " + query.lastError().text());
            qDebug() << "SQL Error:" << query.lastError().text();
        }

        ui->graphicsView->fitInView(scene->sceneRect(), Qt::KeepAspectRatio);
}

void docGraph::showPatientDistribution()
{
    QSqlQuery query;
    if (query.exec("SELECT COUNT(*) as total_patients FROM (SELECT DISTINCT pat_id FROM DocPat_Relation)")) {
        if (query.next()) {
            int totalPatients = query.value("total_patients").toInt();
            ui->patientCountLabel->setText("Total Patients: " + QString::number(totalPatients));
        }
    } else {
        QMessageBox::critical(this, "Error", "Failed to fetch patient count: " + query.lastError().text());
    }
}

void docGraph::createDocClassPieChart()
{
    QPieSeries *series = new QPieSeries();

    QSqlQuery query;
    if (query.exec("SELECT doc_class, COUNT(DISTINCT pat_id) as count FROM DocPat_Relation GROUP BY doc_class")) {
        while (query.next()) {
            QString docClass = query.value("doc_class").toString();
            int count = query.value("count").toInt();
            series->append(docClass, count);
        }
    } else {
        QMessageBox::critical(this, "Error", "Failed to fetch doc_class distribution: " + query.lastError().text());
        return;
    }

    // Add slices to the pie chart series
    pieChart->addSeries(series);
    pieChart->setTitle("Distribution of Doc Classes");
    pieChart->legend()->setVisible(true);
    pieChart->legend()->setAlignment(Qt::AlignRight);

    // You can customize the chart further here
    series->setLabelsVisible(true);
    series->setLabelsPosition(QPieSlice::LabelOutside);

    for (auto slice : series->slices()) {
        slice->setLabel(QString("%1: %2%").arg(slice->label()).arg(100 * slice->percentage(), 0, 'f', 1));
    }

    chartView->setChart(pieChart);
}
