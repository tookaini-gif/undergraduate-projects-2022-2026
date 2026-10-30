#ifndef PATPAGE_H
#define PATPAGE_H

#include <QWidget>

#include <QSqlDatabase>
#include <QSqlQuery>
#include <QSqlError>
#include <QTranslator>

namespace Ui {
class patPage;
}

class patPage : public QWidget
{
    Q_OBJECT

public:
    explicit patPage(QWidget *parent = nullptr);
    ~patPage();

    void setUserId(const QString &userId);


private slots:
    void showTime();
    void on_patProfile_btn_clicked();
    void on_patAppointment_btn_clicked();

    void on_closeBtn1_clicked();

    void on_pushChat_btn_clicked();

    void on_hospital_care_clicked();

    void on_hospital_profile_clicked();

    void on_hospital_activity_clicked();

    void on_patHealthAssesment_btn_clicked();

    void on_EN_clicked();

    void on_CN_clicked();

private:
    Ui::patPage *ui;
    QString userId;
    QString userName;
    QSqlDatabase sqlitedb;

    void loadInfo();

};

#endif // PATPAGE_H
