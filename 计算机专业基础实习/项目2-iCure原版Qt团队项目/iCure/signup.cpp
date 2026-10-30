#include "signup.h"
#include "ui_signup.h"
#include "logindialog.h"

#include <QMessageBox>
#include <QSqlError>
#include <QScreen>
#include <QCryptographicHash>
#include <QRandomGenerator>

signUp::signUp(QWidget *parent) :
    QWidget(parent),
    ui(new Ui::signUp)
//    manager(new QNetworkAccessManager(this))
{
    ui->setupUi(this);

    setWindowFlag(Qt::FramelessWindowHint);
    setAttribute(Qt::WA_TranslucentBackground, true);

    sqlitedb = QSqlDatabase::addDatabase("QSQLITE");
    sqlitedb.setDatabaseName("icure_demo.sqlite");

    if (!sqlitedb.open()) {
        QMessageBox::warning(this, "Error", "Failed to open the database.");
    }

    // Center the window on the screen using QScreen
    QScreen *screen = QGuiApplication::primaryScreen();
    QRect screenGeometry = screen->geometry();
    int x = (screenGeometry.width() - this->width()) / 2;
    int y = (screenGeometry.height() - this->height()) / 2;
    this->move(x, y);

//    // Add a new line edit for email
//    ui->emailLineEdit = new QLineEdit(this);
//    ui->formLayout->addRow("Email:", ui->emailLineEdit);

//    // Add a new line edit for verification code
//    ui->verificationCodeLineEdit = new QLineEdit(this);
//    ui->formLayout->addRow("Verification Code:", ui->verificationCodeLineEdit);

//    // Add a verify button
//    ui->verifyBtn = new QPushButton("Verify Code", this);
//    ui->formLayout->addRow(ui->verifyBtn);

//    connect(ui->verifyBtn, &QPushButton::clicked, this, &signUp::on_verifyBtn_clicked);
}

signUp::~signUp()
{
    delete ui;
}


void signUp::on_signupBtn_clicked()
{

    QString age = ui->age_Line_2->text();
    QString telephone = ui->telephone_Line_2->text();
    QString address = ui->address_Line->toPlainText();
    QString gender = getGender();
    int userId = -1;

    bool ageOk;
    int ageValue = age.toInt(&ageOk);
    if (!age.isEmpty() && (!ageOk || ageValue < 0 || ageValue > 120)) {
        showError("Please enter a valid age (0-120).");
        return;
    }

    QString username = ui->username_Line_2->text();
    QString password = ui->password_Line_2->text();
    QString cpassword = ui->password_Line2_2->text();
    QString identity = getIdentity();

    if (identity.isEmpty()) {
        showError("Please select an identity (Doctor or Patient).");
        return;
    }

    QSqlQuery checkQuery(sqlitedb);
    checkQuery.prepare("SELECT username FROM loginTable WHERE username = :username");
    checkQuery.bindValue(":username", username);
    if (checkQuery.exec() && checkQuery.next()) {
        showError("Username already exists. Please choose a different username.");
        return;
    }

    if (username.isEmpty() || password.isEmpty() || cpassword.isEmpty()) {
        showError("Username and password fields cannot be empty.");
        return;
    }

    if (password != cpassword) {
        showError("Passwords do not match.");
        return;
    }

    if (identity == "doctor") {
        QString doc_class = ui->class_choice->currentText();
        QSqlQuery Dquery(sqlitedb);
        Dquery.prepare("INSERT INTO Doc_Info (doc_name, doc_class, age, gender, telephone, address) "
                      "VALUES (:doc_name, :doc_class, :age, :gender, :telephone, :address)");
        Dquery.bindValue(":doc_name", username);
        Dquery.bindValue(":doc_class", doc_class);
        Dquery.bindValue(":age", ageOk ? ageValue : QVariant(QVariant::Int));
        Dquery.bindValue(":gender", gender);
        Dquery.bindValue(":telephone", telephone);
        Dquery.bindValue(":address", address);

        if (!Dquery.exec()) {
            showError("Failed to insert doctor information. Please try again.");
            return;
        }

        // Retrieve doc_id after successful insertion
        QSqlQuery idQuery(sqlitedb);
        idQuery.prepare("SELECT doc_id FROM Doc_Info WHERE doc_name = :doc_name");
        idQuery.bindValue(":doc_name", username);
        if (idQuery.exec() && idQuery.next()) {
            userId = idQuery.value(0).toInt(); // Assuming doc_id is the first column
        } else {
            showError("Failed to retrieve doctor ID.");
            return;
        }

    } else if (identity == "patient") {
        QSqlQuery Pquery(sqlitedb);
        Pquery.prepare("INSERT INTO Pat_Info (pat_name, age, gender, telephone, address) "
                      "VALUES (:pat_name, :age, :gender, :telephone, :address)");
        Pquery.bindValue(":pat_name", username);
        Pquery.bindValue(":age", ageOk ? ageValue : QVariant(QVariant::Int));
        Pquery.bindValue(":gender", gender);
        Pquery.bindValue(":telephone", telephone);
        Pquery.bindValue(":address", address);

        if (!Pquery.exec()) {
            showError("Failed to insert patient information. Please try again.");
            return;
        }

        // Retrieve pat_id after successful insertion
        QSqlQuery idQuery(sqlitedb);
        idQuery.prepare("SELECT pat_id FROM Pat_Info WHERE pat_name = :pat_name");
        idQuery.bindValue(":pat_name", username);
        if (idQuery.exec() && idQuery.next()) {
            userId = idQuery.value(0).toInt(); // Assuming pat_id is the first column
        } else {
            showError("Failed to retrieve patient ID.");
            return;
        }
    }


    QSqlQuery query(sqlitedb);
    query.prepare("INSERT INTO loginTable (id, username, password, identity) "
                      "VALUES (:id, :username, :password, :identity)");
    query.bindValue(":id", userId);
    query.bindValue(":username", username);
    query.bindValue(":password", password);
    query.bindValue(":identity", identity);

    if (!query.exec()) {
        showError("Failed to sign up. Please try again.");
        return;
    }

    QMessageBox::information(this, tr("Success"),
                             tr("Sign-up successful!"),
                             QMessageBox::Yes);

//    QString email = ui->emailLineEdit->text();
//    if (email.isEmpty() || !email.contains("@")) {
//        showError("Please enter a valid email address.");
//        return;
//    }

//    // Generate and send verification code
//    generateVerificationCode();
//    sendVerificationEmail(email, generatedCode);

//    QMessageBox::information(this, "Verification Required", "A verification code has been sent to your email. Please enter it to complete sign-up.");


}

QString signUp::getGender()
{
    if (ui->cB_male_2->isChecked()) {
        return "male";
    } else if (ui->cB_female_2->isChecked()) {
        return "female";
    } else {
        return "";
    }
}

QString signUp::getIdentity() const
{
    if (ui->cB_doc_2->isChecked() && ui->cB_pat_2->isChecked()) {
        return "";
    } else if (ui->cB_doc_2->isChecked()) {
        return "doctor";
    } else if (ui->cB_pat_2->isChecked()) {
        return "patient";
    } else {
        return "";
    }
}

void signUp::showError(const QString &message)
{
    QMessageBox::warning(this, tr("Warning"), message, QMessageBox::Ok);
}


void signUp::on_closeBtn_clicked()
{
    this->close();
    sqlitedb.close();

    loginDialog *loginPage = new loginDialog();
    loginPage->show();
}

//void signUp::on_verifyBtn_clicked()
//{
//    QString enteredCode = ui->verificationCodeLineEdit->text();
//    if (verifyCode(enteredCode)) {
//        // Proceed with user registration
//        // ... (existing registration code)

//        QMessageBox::information(this, "Success", "Sign-up successful!");

//        loginDialog *loginPage = new loginDialog();
//        this->hide();
//        loginPage->show();
//    } else {
//        showError("Invalid verification code. Please try again.");
//    }
//}

//void signUp::generateVerificationCode()
//{
//    const QString characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
//    const int codeLength = 6;

//    generatedCode.clear();
//    for (int i = 0; i < codeLength; ++i) {
//        int index = QRandomGenerator::global()->bounded(characters.length());
//        generatedCode.append(characters.at(index));
//    }
//}

//void signUp::sendVerificationEmail(const QString &email, const QString &code)
//{
//    // Note: This is a placeholder. In a real application, you would use a proper email service.
//    qDebug() << "Sending verification code" << code << "to" << email;

//    // Here you would typically use an email service API to send the actual email
//    // For demonstration, we're just printing to debug output
//}

//bool signUp::verifyCode(const QString &enteredCode)
//{
//    return enteredCode == generatedCode;
//}
