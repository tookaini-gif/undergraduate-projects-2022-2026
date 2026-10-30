#ifndef PATAPPOINTMENTS_H
#define PATAPPOINTMENTS_H

#include <QDialog>
#include <QSqlDatabase>
#include <QSqlQuery>
#include <QListWidgetItem>
#include <QSqlTableModel>
#include <QModelIndexList>
#include <QSqlRecord>

namespace Ui {
class patAppointments;
}

class patAppointments : public QDialog
{
    Q_OBJECT

public:
    explicit patAppointments(QWidget *parent = nullptr);
    ~patAppointments();

    void setUserInfo(const QString &userId);

private slots:
    void on_backBtn_clicked();
    void on_roomListWidget_itemClicked(QListWidgetItem *item);
    void on_docListWidget_itemClicked(QListWidgetItem *item);
    void populateTimeListWidget(int doc_id);
    void on_pushButton_clicked();
    void on_timelistWidget_itemClicked(QListWidgetItem *item);
    //void deleteSelectedAppointment();

    void on_cancel_btn_clicked();


    void on_laod_btn_clicked();

private:
    Ui::patAppointments *ui;
    QString userId;
    int selectedDocId;
    QString selectedDocname;
    QString patName;
    QString telephone;
    QString selected_apt_time;
    QSqlTableModel *appointmentModel;
    QSqlDatabase sqlitedb;

    void showAppointments();
};

#endif // PATAPPOINTMENTS_H
