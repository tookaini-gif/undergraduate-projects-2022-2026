#include "pathealth.h"
#include "ui_pathealth.h"

#include <QScreen>
#include <QMessageBox>
#include <QtMath>
#include <QFile>

patHealth::patHealth(QWidget *parent) :
    QDialog(parent),
    ui(new Ui::patHealth)
{
    ui->setupUi(this);

    sqlitedb = QSqlDatabase::addDatabase("QSQLITE");
    sqlitedb.setDatabaseName("icure_demo.sqlite");

    if (!sqlitedb.open()) {
        QMessageBox::warning(this, "Error", "Failed to open the database.");
    }

    // set window flags
    setWindowFlag(Qt::FramelessWindowHint);
    setAttribute(Qt::WA_TranslucentBackground, true);

    // Center the window on the screen using QScreen
    QScreen *screen = QGuiApplication::primaryScreen();
    QRect screenGeometry = screen->geometry();
    int x = (screenGeometry.width() - this->width()) / 2;
    int y = (screenGeometry.height() - this->height()) / 2;
    this->move(x, y);

    // Initialize the QLabel
    //eyeTestLabel = new QLabel(this);
    ui->eyeTestLabel->setScaledContents(true);
    ui->eyeTestLabel->hide();  // Initially hide the label

    // Load the image
    QPixmap eyeTestPixmap("../eyetest.jpg");
    ui->eyeTestLabel->setPixmap(eyeTestPixmap);

    // Set the size and position of the label (adjust as needed)
    //ui->eyeTestLabel->setGeometry(50, 50, 400, 300);

}

patHealth::~patHealth()
{
    sqlitedb.close();
    delete ui;
}


void patHealth::setUserId(const QString &userId)
{
    this->userId = userId;

    loadInfo();
}

void patHealth::loadInfo()
{
    QSqlQuery query(sqlitedb);
    query.prepare("SELECT pat_name, age, gender "
                  "FROM Pat_Info WHERE pat_id = :pat_id");
    query.bindValue(":pat_id", userId);

    if (query.exec() && query.next())
    {
        ui->pat_id->setText(userId);
        //this->userName = query.value(0).toString();
        ui->pat_name->setText(query.value(0).toString());
        ui->pat_age->setText(query.value(1).toString());
        ui->pat_gender->setText(query.value(2).toString());
    }
    else
    {
        QMessageBox::warning(this, "Error", "Failed to retrieve doctor information.");
    }

    query.clear();
    if (!query.prepare("SELECT picturePath FROM Pat_Info WHERE pat_id = :pat_id")) {
        //qDebug() << "Query preparation failed: " << query.lastError().text();
        return;
    }

    query.bindValue(":pat_id", userId);

    if (!query.exec()) {
        //qDebug() << "Failed to execute query: " << query.lastError().text();
        //QMessageBox::critical(this, "Query Error", "Failed to execute query: " + query.lastError().text());
        return;
    }

    if (query.next()) {
        QString picturePath = query.value(0).toString();
        QPixmap pix;

        if (!picturePath.isEmpty() && QFile::exists(picturePath)) {
            pix.load(picturePath);
        } else {
            pix.load("../icon1.png");  // Use the correct path for the default image
        }

        ui->icon->setPixmap(pix.scaled(100, 100, Qt::KeepAspectRatio));
    } else {
        QMessageBox::warning(this, "Not Found", "No profile picture found for this user.");
    }
}

double patHealth::calculateBMI(double weight, double height)
{
    return weight / (height * height);
}

int patHealth::evaluateEyeVision(int eyeTestScore)
{
    // Assuming eye test score is out of 100
    if (eyeTestScore >= 90) return 5;
    else if (eyeTestScore >= 80) return 4;
    else if (eyeTestScore >= 70) return 3;
    else if (eyeTestScore >= 60) return 2;
    else return 1;
}

int patHealth::evaluateHeartRate(int heartRate)
{
    // Assuming a normal resting heart rate is between 60-100 bpm
    if (heartRate >= 60 && heartRate <= 100) return 5;
    else if (heartRate > 100 && heartRate <= 110) return 4;
    else if (heartRate > 110 && heartRate <= 120) return 3;
    else if (heartRate > 120 && heartRate <= 130) return 2;
    else return 1;
}

int patHealth::evaluateBodyFat(double bodyFat, QString gender)
{
    if (gender.toLower() == "male") {
        if (bodyFat < 10) return 5;
        else if (bodyFat < 15) return 4;
        else if (bodyFat < 20) return 3;
        else if (bodyFat < 25) return 2;
        else return 1;
    } else {
        if (bodyFat < 18) return 5;
        else if (bodyFat < 23) return 4;
        else if (bodyFat < 28) return 3;
        else if (bodyFat < 33) return 2;
        else return 1;
    }
}



void patHealth::on_evaluate_btn_clicked()
{
    // Get values from UI
    bool ok;
    double weight = ui->weight->text().toDouble(&ok);
    if (!ok) {
        QMessageBox::warning(this, "Input Error", "Invalid weight input.");
        return;
    }

    double height = ui->height->text().toDouble(&ok) / 100.0; // convert cm to m
    if (!ok) {
        QMessageBox::warning(this, "Input Error", "Invalid height input.");
        return;
    }

    int eyeTestScore = ui->eyeTest->text().toInt(&ok);
    if (!ok) {
        QMessageBox::warning(this, "Input Error", "Invalid eye test score input.");
        return;
    }

    int heartRate = ui->heartRate->text().toInt(&ok);
    if (!ok) {
        QMessageBox::warning(this, "Input Error", "Invalid heart rate input.");
        return;
    }

    double bodyFat = ui->bodyFat->text().toDouble(&ok);
    if (!ok) {
        QMessageBox::warning(this, "Input Error", "Invalid body fat input.");
        return;
    }

    QString gender = ui->pat_gender->text();

    // Calculate scores
    double bmi = calculateBMI(weight, height);
    ui->BmiTest->setText(QString::number(bmi, 'f', 2));
    int bmiScore = (bmi >= 18.5 && bmi <= 24.9) ? 5 : (bmi < 18.5 || bmi > 30) ? 1 : 3;
    int eyeScore = evaluateEyeVision(eyeTestScore);
    int heartScore = evaluateHeartRate(heartRate);
    int fatScore = evaluateBodyFat(bodyFat, gender);

    // Calculate overall health score
    int overallScore = (bmiScore + eyeScore + heartScore + fatScore) / 4;

    // Display results
    QString resultMessage = QString("Health Score: %1\n\n").arg(overallScore);
    resultMessage += "Advice:\n";

    if (bmiScore < 5) resultMessage += "- Work on maintaining a healthy BMI through diet and exercise.\n";
    if (eyeScore < 5) resultMessage += "- Consider getting an eye check-up and following eye health practices.\n";
    if (heartScore < 5) resultMessage += "- Focus on cardiovascular health through regular exercise.\n";
    if (fatScore < 5) resultMessage += "- Consider adjusting your diet and exercise routine to manage body fat.\n";

    QMessageBox::information(this, "Health Assessment Results", resultMessage);
}

void patHealth::on_backBtn_clicked()
{
    this->close();
}

void patHealth::on_goEyeTest_clicked()
{
    if (isEyeTestVisible)
   {
       ui->eyeTestLabel->hide();
       isEyeTestVisible = false;
       ui->backBtn->setEnabled(true);
   }
   else
   {
       ui->eyeTestLabel->show();
       isEyeTestVisible = true;
       ui->backBtn->setEnabled(false);
   }
}
