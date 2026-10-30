#include "docprofile.h"
#include "ui_docprofile.h"
#include <QMessageBox>
#include <QScreen>
#include <QPixmap>
#include <QSqlError>
#include <QFile>
#include <QFileDialog>

docProfile::docProfile(QWidget *parent) :
    QDialog(parent),
    ui(new Ui::docProfile)
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

docProfile::~docProfile()
{
    sqlitedb.close();
    delete ui;
}

void docProfile::on_backBtn_clicked()
{
    this->close();
}

void docProfile::setUserId(const QString &userId)
{
    this->userId = userId;
    ui->doc_id->setText(userId);
    loadDoctorInfo();  // Load doctor info when userId is set
}


void docProfile::loadDoctorInfo()
{

    // First query: Fetch information from Doc_Info
    QSqlQuery docQuery(sqlitedb);
    docQuery.prepare("SELECT doc_name, doc_class, age, gender, telephone, address "
                     "FROM Doc_Info WHERE doc_id = :doc_id");
    docQuery.bindValue(":doc_id", userId);

    if (docQuery.exec() && docQuery.next())
    {
        ui->name->setText(docQuery.value(0).toString());
        ui->label_class->setText(docQuery.value(1).toString());
        ui->age->setText(docQuery.value(2).toString());
        ui->gender->setText(docQuery.value(3).toString());
        ui->telephone->setText(docQuery.value(4).toString());
        ui->address->setText(docQuery.value(5).toString());
    }
    else
    {
        QMessageBox::warning(this, "Error", "Failed to retrieve doctor information.");
    }

    // Second query: Fetch username and password from loginTable
    QSqlQuery loginQuery(sqlitedb);
    loginQuery.prepare("SELECT username, password FROM loginTable WHERE id = :id");
    loginQuery.bindValue(":id", userId);

    if (loginQuery.exec() && loginQuery.next())
    {
        ui->username->setText(loginQuery.value(0).toString());
        ui->password->setText(loginQuery.value(1).toString());
    }
    else
    {
        QMessageBox::warning(this, "Error", "Failed to retrieve login information.");
    }

    QSqlQuery query;
    query.prepare("SELECT picturePath FROM Doc_Info WHERE doc_id = :doc_id");
    query.bindValue(":doc_id", userId);

    if (query.exec() && query.next()) {
        QByteArray imagePath = query.value(0).toByteArray();

        QPixmap pixmap;
        if (!imagePath.isEmpty()) {
            pixmap.load(imagePath);
        } else {
            pixmap.load("../icon1.png");  // Default image if no profile picture is available
        }

        ui->icon->setPixmap(pixmap.scaled(150, 150, Qt::KeepAspectRatio));
    } else {
        qDebug() << "Failed to load profile picture: " << query.lastError().text();
        QMessageBox::warning(this, "Error", "Failed to load profile picture for this user.");
    }

}

void docProfile::on_save_clicked()
{

    // Retrieve current values from the UI
    QString newUsername = ui->username->text();
    QString newPassword = ui->password->text();
    QString newName = ui->name->text();
    QString newClass = ui->label_class->text();
    QString newAge = ui->age->text();
    QString newGender = ui->gender->text();
    QString newTelephone = ui->telephone->text();
    QString newAddress = ui->address->toPlainText();

    // Flag to check if username or password changed
    bool usernameChanged = false;
    bool passwordChanged = false;

    // Check if username or password has changed
    QSqlQuery checkQuery(sqlitedb);
    checkQuery.prepare("SELECT username, password FROM loginTable WHERE id = :id");
    checkQuery.bindValue(":id", userId);

    if (checkQuery.exec() && checkQuery.next())
    {
        QString currentUsername = checkQuery.value(0).toString();
        QString currentPassword = checkQuery.value(1).toString();

        if (newUsername != currentUsername) {
            usernameChanged = true;
        }
        if (newPassword != currentPassword) {
            passwordChanged = true;
        }
    }

    // Update Doc_Info table
    QSqlQuery updateDocQuery(sqlitedb);
    updateDocQuery.prepare("UPDATE Doc_Info SET doc_name = :name, doc_class = :class, age = :age, "
                           "gender = :gender, telephone = :telephone, address = :address WHERE doc_id = :doc_id");
    updateDocQuery.bindValue(":name", newName);
    updateDocQuery.bindValue(":class", newClass);
    updateDocQuery.bindValue(":age", newAge);
    updateDocQuery.bindValue(":gender", newGender);
    updateDocQuery.bindValue(":telephone", newTelephone);
    updateDocQuery.bindValue(":address", newAddress);
    updateDocQuery.bindValue(":doc_id", userId);

    if (!updateDocQuery.exec()) {
        QMessageBox::warning(this, "Error", "Failed to update doctor information.");
        return;
    }

    // Update loginTable
    QSqlQuery updateLoginQuery(sqlitedb);
    updateLoginQuery.prepare("UPDATE loginTable SET username = :username, password = :password WHERE id = :id");
    updateLoginQuery.bindValue(":username", newUsername);
    updateLoginQuery.bindValue(":password", newPassword);
    updateLoginQuery.bindValue(":id", userId);

    if (!updateLoginQuery.exec()) {
        QMessageBox::warning(this, "Error", "Failed to update login information.");
        return;
    }

    // Ask user for confirmation if username or password has changed
    if (usernameChanged || passwordChanged) {
        QString message = "Your changes have been saved.\n";
        if (usernameChanged) {
            message += "Do you want to change your username?\n";
        }
        if (passwordChanged) {
            message += "Do you want to change your password?";
        }

        QMessageBox::StandardButton reply;
        reply = QMessageBox::question(this, "Confirm Changes", message,
                                      QMessageBox::Yes | QMessageBox::No);

        if (reply == QMessageBox::Yes) {
            // Proceed with saving the changes to username and/or password
            QSqlQuery updateLoginQuery(sqlitedb);
            updateLoginQuery.prepare("UPDATE loginTable SET username = :username, password = :password WHERE id = :id");
            updateLoginQuery.bindValue(":username", newUsername);
            updateLoginQuery.bindValue(":password", newPassword);
            updateLoginQuery.bindValue(":id", userId);

            if (!updateLoginQuery.exec()) {
                QMessageBox::warning(this, "Error", "Failed to update login information.");
            } else {
                QMessageBox::information(this, "Success", "Your username and/or password has been updated.");
            }
        } else {
            QMessageBox::information(this, "No Changes", "Username and password remain unchanged.");
        }
    } else {
        QMessageBox::information(this, "Success", "Your changes have been saved.");
    }

}

void docProfile::on_load_btn_clicked()
{
    loadDoctorInfo();
}

void docProfile::on_uploadicon_Btn_clicked()
{
    QString filePath = QFileDialog::getOpenFileName(this, "Select Profile Picture", "", "Images (*.png *.jpg *.bmp)");

    if (filePath.isEmpty()) {
        QMessageBox::warning(this, "No File Selected", "Please select an image file.");
        return;
    }

    QFile file(filePath);
    if (!file.open(QIODevice::ReadOnly)) {
        QMessageBox::critical(this, "File Error", "Unable to open the selected file.");
        return;
    }

    QByteArray picturePath = file.readAll();
    file.close();

    QSqlQuery query;
    query.clear();
    query.prepare("UPDATE Doc_Info SET picturePath = :picturePath WHERE doc_id = :doc_id");
    query.bindValue(":picturePath", filePath);
    query.bindValue(":doc_id", userId);

    if (!query.exec()) {
        qDebug() << "Failed to update profile picture: " << query.lastError().text();
        QMessageBox::critical(this, "Database Error", "Failed to upload the image to the database.");
    } else {
        QMessageBox::information(this, "Success", "Profile picture updated successfully.");
        loadDoctorInfo();  // Reload the profile picture
    }


}



