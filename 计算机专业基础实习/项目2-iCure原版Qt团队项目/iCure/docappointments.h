#ifndef DOCAPPOINTMENTS_H
#define DOCAPPOINTMENTS_H

#include <QDialog>
#include "docpage.h"
#include <QSqlDatabase>
#include <QSqlQuery>
#include <QListWidgetItem>
#include <QSqlTableModel>
#include <QModelIndexList>
#include <QSqlRecord>

namespace Ui {
class docAppointments;
}

class docAppointments : public QDialog
{
    Q_OBJECT

public:
    explicit docAppointments(QWidget *parent = nullptr);
    ~docAppointments();
    void setUserId(const QString &userId);

private slots:
    void on_backBtn_clicked();

    void on_laod_btn_clicked();

    void on_cancel_btn_clicked();

private:
    Ui::docAppointments *ui;
    QString userId;
    QSqlTableModel *appointmentModel;
    QSqlDatabase sqlitedb;

    void showAppointments();
};

#endif // DOCAPPOINTMENTS_H
