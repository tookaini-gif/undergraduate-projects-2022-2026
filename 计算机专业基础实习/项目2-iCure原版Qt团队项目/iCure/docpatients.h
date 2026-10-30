#ifndef DOCPATIENTS_H
#define DOCPATIENTS_H

#include <QDialog>
#include <docpage.h>
#include <QSqlDatabase>
#include <QListWidgetItem>
#include <QSqlQuery>
#include <QDebug>
#include <QSqlError>

namespace Ui {
class docPatients;
}

class docPatients : public QDialog
{
    Q_OBJECT

public:
    explicit docPatients(QWidget *parent = nullptr);
    ~docPatients();

    void setUserId(const QString &userId);

private slots:
    void on_backBtn_clicked();
    void on_patient_List_itemClicked(QListWidgetItem *item);
    void on_saveBtn_clicked();

private:
    Ui::docPatients *ui;
    QString userId;
    QSqlDatabase sqlitedb;

    void loadPatientsInfo();
};

#endif // DOCPATIENTS_H
