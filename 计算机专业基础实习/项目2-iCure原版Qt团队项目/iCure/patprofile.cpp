#include "patprofile.h"
#include "ui_patprofile.h"
#include <QString>
#include <QMessageBox>
#include <QScreen>
#include <QPixmap>
#include <QSqlError>
#include <QFile>
#include <QFileDialog>

patProfile::patProfile(QWidget *parent) :
    QDialog(parent),
    ui(new Ui::patProfile)
{
    ui->setupUi(this);

    // Initialize and open the database connection
    sqlitedb = QSqlDatabase::addDatabase("QSQLITE");
    sqlitedb.setDatabaseName("icure_demo.sqlite");

    if (!sqlitedb.open()) {
        QMessageBox::warning(this, "Error", "Failed to open the database.");
    }

    // set window flags
    setWindowFlag(Qt::FramelessWindowHint);
    setAttribute(Qt::WA_TranslucentBackground, true);

    // Center the window on the screen using QScreen
    QScreen *screen = QGuiApplication::primaryScreen();
    QRect screenGeometry = screen->geometry();
    int x = (screenGeometry.width() - this->width()) / 2;
    int y = (screenGeometry.height() - this->height()) / 2;
    this->move(x, y);


}

patProfile::~patProfile()
{
    sqlitedb.close();
    delete ui;
}

void patProfile::on_backBtn_clicked()
{
    this->close();
}

void patProfile::setUserId(const QString &userId)
{
    this->userId = userId;
    ui->pat_id->setText(userId);
    loadPatientInfo();  // Load doctor info when userId is set
}


void patProfile::loadPatientInfo()
{

    // First query: Fetch information from Pat_Info
    QSqlQuery patQuery(sqlitedb);
    patQuery.prepare("SELECT pat_name, age, gender, telephone, address "
                     "FROM Pat_Info WHERE pat_id = :pat_id");
    patQuery.bindValue(":pat_id", userId);

    if (patQuery.exec() && patQuery.next())
    {
        ui->name->setText(patQuery.value(0).toString());
        ui->age->setText(patQuery.value(1).toString());
        ui->gender->setText(patQuery.value(2).toString());
        ui->telephone->setText(patQuery.value(3).toString());
        ui->address->setText(patQuery.value(4).toString());
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
    query.prepare("SELECT picturePath FROM Pat_Info WHERE pat_id = :pat_id");
    query.bindValue(":pat_id", userId);

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

void patProfile::on_save_clicked()
{

    // Retrieve current values from the UI
    QString newUsername = ui->username->text();
    QString newPassword = ui->password->text();
    QString newName = ui->name->text();
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

    // Update Pat_Info table
    QSqlQuery updatePatQuery(sqlitedb);
    updatePatQuery.prepare("UPDATE Pat_Info SET pat_name = :name, age = :age, "
                           "gender = :gender, telephone = :telephone, address = :address WHERE pat_id = :pat_id");
    updatePatQuery.bindValue(":name", newName);
    updatePatQuery.bindValue(":age", newAge);
    updatePatQuery.bindValue(":gender", newGender);
    updatePatQuery.bindValue(":telephone", newTelephone);
    updatePatQuery.bindValue(":address", newAddress);
    updatePatQuery.bindValue(":pat_id", userId);

    if (!updatePatQuery.exec()) {
        QMessageBox::warning(this, "Error", "Failed to update patient information.");
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

void patProfile::on_load_btn_clicked()
{
    loadPatientInfo();
}

void patProfile::on_uploadicon_Btn_clicked()
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
    query.prepare("UPDATE Pat_Info SET picturePath = :picturePath WHERE pat_id = :pat_id");
    query.bindValue(":picturePath", filePath);
    query.bindValue(":pat_id", userId);

    if (!query.exec()) {
        qDebug() << "Failed to update profile picture: " << query.lastError().text();
        QMessageBox::critical(this, "Database Error", "Failed to upload the image to the database.");
    } else {
        QMessageBox::information(this, "Success", "Profile picture updated successfully.");
        loadPatientInfo();  // Reload the profile picture
    }


}
