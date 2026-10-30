#ifndef DOCPROFILE_H
#define DOCPROFILE_H

#include <QDialog>
#include <docpage.h>
#include <QSqlDatabase>
#include <QSqlQuery>
#include <QDebug>

namespace Ui {
class docProfile;
}

class docProfile : public QDialog
{
    Q_OBJECT

public:
    explicit docProfile(QWidget *parent = nullptr);
    ~docProfile();

    void setUserId(const QString &userId);

private slots:
    void on_backBtn_clicked();
    void on_save_clicked();
    void on_load_btn_clicked();

    void on_uploadicon_Btn_clicked();

private:
    Ui::docProfile *ui;
    QString userId;
    QSqlDatabase sqlitedb;

    void loadDoctorInfo();
};

#endif // DOCPROFILE_H
