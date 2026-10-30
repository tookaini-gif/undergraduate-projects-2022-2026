#ifndef DOCPAGE_H
#define DOCPAGE_H

#include <QWidget>
#include "docappointments.h"
#include "docprofile.h"
#include <QSqlDatabase>
#include <QSqlQuery>
#include <QTranslator>

namespace Ui {
class docPage;
}

class docPage : public QWidget
{
    Q_OBJECT

public:
    explicit docPage(QWidget *parent = nullptr);
    ~docPage();

    void setUserId(const QString &userId);

private slots:
    void showTime();
    void on_docProfile_btn_clicked();
    void on_docAppointment_btn_clicked();
    void on_closeBtn1_clicked();
    void on_Notice_btn_clicked();
    void on_docPatients_btn_clicked();

    void on_docChats_btn_clicked();
    void on_docGraph_btn_clicked();

    void on_About_btn_clicked();

    void on_Activity_btn_clicked();

    void on_EN_clicked();

    void on_CN_clicked();

private:
    Ui::docPage *ui;
    QString userId;
    QString userName;
    QSqlDatabase sqlitedb;

    void loadInfo();
};

#endif // DOCPAGE_H
