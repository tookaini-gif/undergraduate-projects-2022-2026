#include "docappointments.h"
#include "ui_docappointments.h"

#include <QMessageBox>
#include <QDateTime>
#include <QDebug>
#include <QSqlError>

docAppointments::docAppointments(QWidget *parent) :
    QDialog(parent),
    ui(new Ui::docAppointments)
{
    ui->setupUi(this);

    // set window flags
    setWindowFlag(Qt::FramelessWindowHint);
    setAttribute(Qt::WA_TranslucentBackground, true);

    // Initialize and open the database connection
    sqlitedb = QSqlDatabase::addDatabase("QSQLITE");
    sqlitedb.setDatabaseName("icure_demo.sqlite");

    if (!sqlitedb.open()) {
        QMessageBox::warning(this, "Error", "Failed to open the database.");
    }

}

docAppointments::~docAppointments()
{
    delete ui;
}

void docAppointments::on_backBtn_clicked()
{
    this->close();
}

void docAppointments::setUserId(const QString &userId)
{
    this->userId = userId;
    showAppointments();

}

void docAppointments::showAppointments()
{
    int userid = userId.toInt();
    // Create and set up the model
    appointmentModel = new QSqlTableModel(this, sqlitedb);
    appointmentModel->setTable("appointment");
    appointmentModel->setFilter(QString("doc_id = %1").arg(userid));
    appointmentModel->setSort(3, Qt::AscendingOrder); // Sort by apt_time
    appointmentModel->select();

    // Set headers
    appointmentModel->setHeaderData(0, Qt::Horizontal, tr("ID"));
    appointmentModel->setHeaderData(1, Qt::Horizontal, tr("Doctor ID"));
    appointmentModel->setHeaderData(2, Qt::Horizontal, tr("Doctor Name"));
    appointmentModel->setHeaderData(3, Qt::Horizontal, tr("Appointment Time"));
    appointmentModel->setHeaderData(4, Qt::Horizontal, tr("Patient Name"));
    appointmentModel->setHeaderData(5, Qt::Horizontal, tr("Patient Telephone"));

    // Set the model to the table view
    ui->apt_table->setModel(appointmentModel);

    // Hide the ID and Doctor ID columns
    ui->apt_table->hideColumn(0);
    ui->apt_table->hideColumn(1);

    // Resize columns to content
    ui->apt_table->resizeColumnsToContents();

    // Enable sorting
    ui->apt_table->setSortingEnabled(true);

    // Allow selection of entire rows only
    ui->apt_table->setSelectionBehavior(QAbstractItemView::SelectRows);
    ui->apt_table->setSelectionMode(QAbstractItemView::SingleSelection);
}

void docAppointments::on_laod_btn_clicked()
{
    showAppointments();
}

void docAppointments::on_cancel_btn_clicked()
{
    // Get the selected row
    QModelIndex currentIndex = ui->apt_table->currentIndex();
    if (!currentIndex.isValid()) {
        QMessageBox::warning(this, "Warning", "Please select an appointment to cancel.");
        return;
    }

    // Get the appointment ID from the hidden column
    int appointmentId = appointmentModel->data(appointmentModel->index(currentIndex.row(), 0)).toInt();

    // Confirm cancellation
    QMessageBox::StandardButton reply = QMessageBox::question(this, "Confirm Cancellation",
                                                              "Are you sure you want to cancel this appointment?",
                                                              QMessageBox::Yes | QMessageBox::No);
    if (reply == QMessageBox::Yes) {
        // Remove the appointment from the database
        QSqlQuery query(sqlitedb);
        query.prepare("DELETE FROM appointment WHERE id = :id");
        query.bindValue(":id", appointmentId);

        if (query.exec()) {
            QMessageBox::information(this, "Success", "Appointment cancelled successfully.");
            // Refresh the model to show updated data
            appointmentModel->select();
        } else {
            QMessageBox::warning(this, "Error", "Failed to cancel appointment: " + query.lastError().text());
        }
    }
}
