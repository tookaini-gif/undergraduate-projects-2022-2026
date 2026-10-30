#include "patappointments.h"
#include "ui_patappointments.h"

#include <QScreen>
#include <QMessageBox>
#include <QDateTime>
#include <QDebug>
#include <QSqlError>

patAppointments::patAppointments(QWidget *parent) :
    QDialog(parent),
    ui(new Ui::patAppointments)
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

    QSqlQuery query("SELECT DISTINCT doc_class FROM DocPat_Relation");
    while (query.next()) {
        QString docClass = query.value(0).toString();
        ui->roomListWidget->addItem(docClass);
    }

}

patAppointments::~patAppointments()
{
    sqlitedb.close();
    delete ui;
}

void patAppointments::on_backBtn_clicked()
{
    this->close();
}

void patAppointments::setUserInfo(const QString &userId)
{
    this->userId = userId;

    QSqlQuery query;
    query.prepare("SELECT pat_name, telephone FROM Pat_Info WHERE pat_id = :pat_id");
    query.bindValue(":pat_id", userId);

    if (query.exec() && query.next()) {
        patName = query.value(0).toString();
        telephone = query.value(1).toString();

        ui->label_name->setText(patName);
        ui->label_telephone->setText(telephone);
    } else {
        QMessageBox::warning(this, "Error", "Failed to retrieve the patient name and telephone.");
        return;
    }

    showAppointments();
}

void patAppointments::on_roomListWidget_itemClicked(QListWidgetItem *item)
{
    QString selectedDocClass = item->text();

    // Clear the docListWidget before adding new items
    ui->docListWidget->clear();

    // Query to get the doc_name related to the selected doc_class
    QSqlQuery query;
    query.prepare("SELECT doc_name FROM Doc_Info WHERE doc_class = :doc_class");
    query.bindValue(":doc_class", selectedDocClass);

    if (query.exec()) {
        while (query.next()) {
            QString docName = query.value(0).toString();
            ui->docListWidget->addItem(docName);
        }
    } else {
        QMessageBox::warning(this, "Error", "Failed to retrieve doctor names.");
    }
}

void patAppointments::on_docListWidget_itemClicked(QListWidgetItem *item)
{
    // Get the selected doctor's name
    selectedDocname = item->text();

    // Query the database to get the doc_id for the selected doctor
    QSqlQuery query;
    query.prepare("SELECT doc_id FROM Doc_Info WHERE doc_name = :doc_name");
    query.bindValue(":doc_name", selectedDocname);

    int docId = -1; // Initialize to an invalid ID
    if (query.exec() && query.next()) {
        docId = query.value(0).toInt();
    } else {
        QMessageBox::warning(this, "Error", "Failed to retrieve the doctor's ID.");
        return;
    }

    // Populate the time list widget with available times for this doctor
    populateTimeListWidget(docId);

    // Save the selected doctor information for later use when booking the appointment
    selectedDocId = docId;
    selectedDocname = item->text();
}

void patAppointments::populateTimeListWidget(int doc_id)
{
    // Clear the time list widget before adding new items
    ui->timelistWidget->clear();

    // Define the time slots you want to offer (example: 9:00 AM to 5:00 PM, every hour)
    QStringList timeSlots;
    for (int hour = 9; hour <= 17; ++hour) {
        timeSlots.append(QString("%1:00").arg(hour, 2, 10, QLatin1Char('0')));
    }

    // Query the database for booked times for the selected doctor
    QSqlQuery query;
    query.prepare("SELECT apt_time FROM appointment WHERE doc_id = :doc_id");
    query.bindValue(":doc_id", doc_id);

    if (query.exec()) {
        QStringList bookedTimes;
        while (query.next()) {
            bookedTimes.append(query.value(0).toString());
        }

        // Add only the available times to the timelistWidget
        foreach (const QString &timeSlot, timeSlots) {
            if (!bookedTimes.contains(timeSlot)) {
                ui->timelistWidget->addItem(timeSlot);
            }
        }
    } else {
        QMessageBox::warning(this, "Error", "Failed to retrieve booked times.");
    }
}


void patAppointments::on_timelistWidget_itemClicked(QListWidgetItem *item)
{
    selected_apt_time = item->text();
}

void patAppointments::on_pushButton_clicked()
{

    QSqlQuery query;
    query.prepare("INSERT INTO appointment (doc_id, doc_name, apt_time, pat_name, pat_telephone) "
                  "VALUES (:doc_id, :doc_name, :apt_time, :pat_name, :pat_telephone)");
    query.bindValue(":doc_id", selectedDocId);
    query.bindValue(":doc_name", selectedDocname);
    query.bindValue(":apt_time", selected_apt_time);
    query.bindValue(":pat_name", patName);
    query.bindValue(":pat_telephone", telephone);

    if (!query.exec()) {
        QMessageBox::warning(this, "Error", "Failed to book the appointment.");
    } else {
        QMessageBox::information(this, "Success", "Appointment booked successfully.");

        // Refresh the available times (to reflect the newly booked slot)
        populateTimeListWidget(selectedDocId);
    }
}


void patAppointments::on_cancel_btn_clicked()
{
    QItemSelectionModel *selectionModel = ui->appointmentTable->selectionModel();
    if (!selectionModel) {
        qDebug() << "No selection model found.";
        return;
    }

    QModelIndexList selectedIndexes = selectionModel->selectedRows();
    if (selectedIndexes.isEmpty()) {
        QMessageBox::warning(this, tr("Warning"), tr("No row selected to delete."));
        return;
    }

    // Confirm deletion
    QMessageBox::StandardButton reply;
    reply = QMessageBox::question(this, tr("Confirm Delete"), tr("Are you sure you want to delete the selected row(s)?"),
                                  QMessageBox::Yes|QMessageBox::No);
    if (reply == QMessageBox::No) {
        return;
    }

    // Delete selected rows
    for (const QModelIndex &index : selectedIndexes) {
        appointmentModel->removeRow(index.row());
    }

    // Commit changes to the database
    if (!appointmentModel->submitAll()) {
        qDebug() << "Failed to submit changes to the database:" << appointmentModel->lastError().text();
        QMessageBox::critical(this, tr("Error"), tr("Failed to delete the selected appointment(s)."));
    } else {
        qDebug() << "Selected rows deleted successfully.";
    }

    // Reload data in the table view
    showAppointments();
}

void patAppointments::showAppointments()
{

    // Set up the model to interact with the appointmentTable
    appointmentModel = new QSqlTableModel(this, sqlitedb);
    appointmentModel->setTable("appointment");
    appointmentModel->setFilter(QString("pat_name = '%1'").arg(patName));
    appointmentModel->setSort(3, Qt::AscendingOrder); // Sort by apt_time
    appointmentModel->select();  // Load data from the table

    // Set headers
    appointmentModel->setHeaderData(0, Qt::Horizontal, tr("ID"));
    appointmentModel->setHeaderData(1, Qt::Horizontal, tr("Doctor ID"));
    appointmentModel->setHeaderData(2, Qt::Horizontal, tr("Doctor Name"));
    appointmentModel->setHeaderData(3, Qt::Horizontal, tr("Appointment Time"));
    appointmentModel->setHeaderData(4, Qt::Horizontal, tr("Patient Name"));
    appointmentModel->setHeaderData(5, Qt::Horizontal, tr("Patient Telephone"));

    // Set the model to the table view
    ui->appointmentTable->setModel(appointmentModel);

    // Hide the ID and Doctor ID columns
    ui->appointmentTable->hideColumn(0);
    ui->appointmentTable->hideColumn(1);

    // Resize columns to content
    ui->appointmentTable->resizeColumnsToContents();

    // Enable sorting
    ui->appointmentTable->setSortingEnabled(true);

    // Set the model for the QTableView
    ui->appointmentTable->setSelectionBehavior(QAbstractItemView::SelectRows);  // Allow selection of rows
    ui->appointmentTable->setSelectionMode(QAbstractItemView::SingleSelection); // Allow only one row to be selected
    ui->appointmentTable->setEditTriggers(QAbstractItemView::NoEditTriggers);   // Make the table view read-only
}

void patAppointments::on_laod_btn_clicked()
{
    showAppointments();
}
