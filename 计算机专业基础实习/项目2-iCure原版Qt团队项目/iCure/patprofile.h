#ifndef PATPROFILE_H
#define PATPROFILE_H

#include <QDialog>
#include "patpage.h"
#include <QSqlDatabase>
#include <QSqlQuery>
#include <QDebug>

namespace Ui {
class patProfile;
}

class patProfile : public QDialog
{
    Q_OBJECT

public:
    explicit patProfile(QWidget *parent = nullptr);
    ~patProfile();

    void setUserId(const QString &userId);

private slots:
    void on_backBtn_clicked();
    void on_save_clicked();
    void on_load_btn_clicked();
    void on_uploadicon_Btn_clicked();

private:
    Ui::patProfile *ui;
    QString userId;
    QSqlDatabase sqlitedb;

    void loadPatientInfo();
};

#endif // PATPROFILE_H
