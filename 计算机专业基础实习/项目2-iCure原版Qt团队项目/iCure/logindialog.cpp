#include "logindialog.h"
#include "ui_logindialog.h"
#include "docpage.h"
#include "patpage.h"
#include "signup.h"
#include <QMessageBox>
#include <QPixmap>
#include <QScreen>

loginDialog::loginDialog(QWidget *parent)
    : QMainWindow(parent)
    , ui(new Ui::loginDialog)
{
    ui->setupUi(this);

    sqlitedb = QSqlDatabase::addDatabase("QSQLITE");
    sqlitedb.setDatabaseName("icure_demo.sqlite");

    if (!sqlitedb.open()) {
        QMessageBox::warning(this, "Error", "Failed to open the database.");
    }

    QPixmap pix("../hospital.jpg");
    ui->label_pic->setPixmap(pix.scaled(400,400,Qt::KeepAspectRatio));

    // connect close button
    connect(ui->closeBtn, &QPushButton::clicked, this, &loginDialog::close);

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

loginDialog::~loginDialog()
{
    sqlitedb.close();
    delete ui;
}


void loginDialog::on_loginBtn_clicked()
{
    QString username = ui->usrLineEdit->text();
    QString password = ui->pwdLineEdit->text();

    QSqlQuery query(sqlitedb);
    query.prepare("SELECT * FROM loginTable WHERE username = :username AND password = :password");
    query.bindValue(":username", username);
    query.bindValue(":password", password);

    if (query.exec()){
        if(query.next()){

            // Store the ID and identity
            userId = query.value(0).toString();
            QString userIdentity = query.value(3).toString();

            // Navigate to the appropriate main page based on identity
            if (userIdentity == "doctor") {
                docPage *doctorPage = new docPage();
                this->hide();
                doctorPage->setUserId(userId);
                doctorPage->show();

            } else if (userIdentity == "patient") {
                patPage *patientPage = new patPage();
                this->hide();
                patientPage->setUserId(userId);
                patientPage->show();
            }



            //accept();  // Close the dialog after successful login
        }
        else {
            QMessageBox::warning(this, tr("Warning"),
                                 tr("Invalid username or password"),
                                 QMessageBox::Yes);
        }
    }
    else {
            QMessageBox::warning(this, tr("Warning"),
                                 tr("Login failed due to database error"),
                                 QMessageBox::Yes);
        }

}

void loginDialog::on_gosignupBtn_clicked()
{
    signUp *signupPage = new signUp();
    this->close();
    signupPage->show();
}
