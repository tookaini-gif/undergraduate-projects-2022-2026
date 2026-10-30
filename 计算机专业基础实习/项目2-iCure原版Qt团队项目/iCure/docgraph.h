#ifndef DOCGRAPH_H
#define DOCGRAPH_H

#include <QDialog>
#include <QSqlDatabase>
#include <QGraphicsScene>
#include <QGraphicsView>
#include <QListWidgetItem>
#include <QtCharts>

namespace Ui {
class docGraph;
}

class docGraph : public QDialog
{
    Q_OBJECT

public:
    explicit docGraph(QWidget *parent = nullptr);
    ~docGraph();

private slots:
    void on_backBtn_clicked();
    void on_classListWidget_itemClicked(QListWidgetItem *item);
    void on_showPieChartBtn_clicked();

private:
    Ui::docGraph *ui;
    QSqlDatabase db;
    QGraphicsScene *scene;
    QChart *pieChart;
    QChartView *chartView;

    void loadDocClasses();
    void showSymptomGraph(const QString &docClass);
    void showPatientDistribution();
    void createDocClassPieChart();
    void toggleChartView(bool showPieChart);

};

#endif // DOCGRAPH_H
