#include "docpatients.h"
#include "ui_docpatients.h"

#include <QMessageBox>
#include <QScreen>

docPatients::docPatients(QWidget *parent) :
    QDialog(parent),
    ui(new Ui::docPatients)
{
    ui->setupUi(this);

    // set window flags
    setWindowFlag(Qt::FramelessWindowHint);
    setAttribute(Qt::WA_TranslucentBackground, true);

    // Center the window on the screen using QScreen
    QScreen *screen = QGuiApplication::primaryScreen();
    QRect screenGeometry = screen->geometry();
    int x = (screenGeometry.width() - this->width()) / 2;
    int y = (screenGeometry.height() - this->height()) / 2;
    this->move(x, y);

    // Initialize and open the database connection
    sqlitedb = QSqlDatabase::addDatabase("QSQLITE");
    sqlitedb.setDatabaseName("icure_demo.sqlite");

    if (!sqlitedb.open()) {
        QMessageBox::warning(this, "Error", "Failed to open the database.");
    }

}

docPatients::~docPatients()
{
    sqlitedb.close();
    delete ui;
}

void docPatients::on_backBtn_clicked()
{
    this->close();
}

void docPatients::setUserId(const QString &userId)
{
    this->userId = userId;
    loadPatientsInfo();  // Load patients info when userId is set
}


void docPatients::loadPatientsInfo()
{

    // First, get the patient IDs associated with the doctor
    QSqlQuery query(sqlitedb);
    query.prepare("SELECT pat_id FROM DocPat_Relation WHERE doc_id = :doc_id");
    query.bindValue(":doc_id", userId);

    if (query.exec())
    {
        while (query.next())
        {
            QString patientId = query.value(0).toString();

            // Now, get the patient's name using the patient ID
            QSqlQuery patientQuery(sqlitedb);
            patientQuery.prepare("SELECT pat_name FROM Pat_Info WHERE pat_id = :pat_id");
            patientQuery.bindValue(":pat_id", patientId);

            if (patientQuery.exec() && patientQuery.next())
            {
                QString patientName = patientQuery.value(0).toString();
                // Add the patient's name to the QListWidget
                ui->patient_List->addItem(patientName);
            }
        }
    }
    else
    {
        QMessageBox::warning(this, "Error", "Failed to retrieve patient information.");
    }


}


void docPatients::on_patient_List_itemClicked(QListWidgetItem *item)
{
    QString patientName = item->text();

    // First, fetch the patient ID based on the name
    QSqlQuery query(sqlitedb);
    query.prepare("SELECT pat_id, age, gender FROM Pat_Info WHERE pat_name = :pat_name");
    query.bindValue(":pat_name", patientName);

    if (query.exec() && query.next())
    {
        QString patientId = query.value(0).toString();
        QString age = query.value(1).toString();
        QString gender = query.value(2).toString();

        // Now, fetch symptoms, advice, prescription, and treatment_status from DocPatientRelation
        QSqlQuery relationQuery(sqlitedb);
        relationQuery.prepare("SELECT symptoms, advice, prescription, treatment_status "
                              "FROM DocPat_Relation WHERE pat_id = :pat_id AND doc_id = :doc_id");
        relationQuery.bindValue(":pat_id", patientId);
        relationQuery.bindValue(":doc_id", userId);

        if (relationQuery.exec() && relationQuery.next())
        {
            QString symptoms = relationQuery.value(0).toString();
            QString advice = relationQuery.value(1).toString();
            QString prescription = relationQuery.value(2).toString();
            QString treatmentStatus = relationQuery.value(3).toString();

            // Display the information on the UI
            ui->label_name->setText(patientName);
            ui->label_age->setText(age);
            ui->label_gender->setText(gender);
            ui->text_symptoms->setText(symptoms);
            ui->text_advice->setText(advice);
            ui->text_prescription->setText(prescription);
            //ui->label_treatmentStatus->setText(treatmentStatus);
            ui->text_prescription->setText(prescription);

            // Set the current index of the QComboBox based on the treatment status
            int index = ui->status_cB->findText(treatmentStatus);
            if (index != -1) {
                ui->status_cB->setCurrentIndex(index);
            } else {
                // If the status is not found in the combo box, set it to the first item
                ui->status_cB->setCurrentIndex(0);
            }
        }

    }
    else
    {
        QMessageBox::warning(this, "Error", "Failed to retrieve patient information from Pat_Info.");
    }

}

void docPatients::on_saveBtn_clicked()
{
    QString patientName = ui->label_name->text();

    QSqlQuery patientQuery(sqlitedb);
    patientQuery.prepare("SELECT pat_id FROM Pat_Info WHERE pat_name = :pat_name");
    patientQuery.bindValue(":pat_name", patientName);

    if (patientQuery.exec() && patientQuery.next())
    {
        QString patientId = patientQuery.value(0).toString();

        // Prepare the update query
        QSqlQuery updateQuery(sqlitedb);
        updateQuery.prepare("UPDATE DocPat_Relation SET "
                            "symptoms = :symptoms, "
                            "advice = :advice, "
                            "prescription = :prescription, "
                            "treatment_status = :treatment_status "
                            "WHERE pat_id = :pat_id AND doc_id = :doc_id");

        // Bind the values
        updateQuery.bindValue(":symptoms", ui->text_symptoms->toPlainText());
        updateQuery.bindValue(":advice", ui->text_advice->toPlainText());
        updateQuery.bindValue(":prescription", ui->text_prescription->toPlainText());
        updateQuery.bindValue(":treatment_status", ui->status_cB->currentText());
        updateQuery.bindValue(":pat_id", patientId);
        updateQuery.bindValue(":doc_id", userId);

        // Execute the query
        if (updateQuery.exec())
        {
            QMessageBox::information(this, "Success", "Patient information updated successfully.");
        }
        else
        {
            QMessageBox::warning(this, "Error", "Failed to update patient information: " + updateQuery.lastError().text());
        }
    }
    else
    {
        QMessageBox::warning(this, "Error", "Failed to retrieve patient ID: " + patientQuery.lastError().text());
    }
}
