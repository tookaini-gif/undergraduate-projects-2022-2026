#ifndef SIGNUP_H
#define SIGNUP_H

#include <QWidget>
#include <QtSql/QSqlDatabase>
#include <QDebug>
#include <QSqlQuery>
//#include <QNetworkAccessManager>
//#include <QNetworkReply>
//#include <QUrlQuery>


namespace Ui {
class signUp;
}

class signUp : public QWidget
{
    Q_OBJECT

public:
    explicit signUp(QWidget *parent = nullptr);
    ~signUp();

private slots:
    void on_signupBtn_clicked();

    QString getGender();
    QString getIdentity() const;
    void showError(const QString &message);

    //void on_signupBtn_clicked();
//    void on_verifyBtn_clicked();

    void on_closeBtn_clicked();

private:
    Ui::signUp *ui;
    QSqlDatabase sqlitedb;
//    QString generatedCode;
//    QNetworkAccessManager *manager;
//    void generateVerificationCode();
//    void sendVerificationEmail(const QString &email, const QString &code);
//    bool verifyCode(const QString &enteredCode);
};

#endif // SIGNUP_H
