#ifndef PATHEALTH_H
#define PATHEALTH_H

#include <QDialog>
#include <QSqlDatabase>
#include <QSqlQuery>
#include <QDebug>

namespace Ui {
class patHealth;
}

class patHealth : public QDialog
{
    Q_OBJECT

public:
    explicit patHealth(QWidget *parent = nullptr);
    ~patHealth();

    void setUserId(const QString &userId);

private slots:
    void on_evaluate_btn_clicked();

    void on_backBtn_clicked();

    void on_goEyeTest_clicked();

private:
    Ui::patHealth *ui;
    QString userId;
    QSqlDatabase sqlitedb;
    bool isEyeTestVisible;

    void loadInfo();
    double calculateBMI(double weight, double height);
    int evaluateEyeVision(int eyeTestScore);
    int evaluateHeartRate(int heartRate);
    int evaluateBodyFat(double bodyFat, QString gender);
};

#endif // PATHEALTH_H
