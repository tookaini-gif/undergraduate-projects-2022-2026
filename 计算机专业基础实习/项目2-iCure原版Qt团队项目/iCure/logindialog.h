#ifndef LOGINDIALOG_H
#define LOGINDIALOG_H

#include <QMainWindow>
#include <QtSql/QSqlDatabase>
#include <QDebug>
#include <QSqlQuery>
#include <QString>

QT_BEGIN_NAMESPACE
namespace Ui { class loginDialog; }
QT_END_NAMESPACE

class loginDialog : public QMainWindow
{
    Q_OBJECT

public:
    loginDialog(QWidget *parent = nullptr);
    ~loginDialog();

private slots:
    void on_loginBtn_clicked();
    void on_gosignupBtn_clicked();

private:
    Ui::loginDialog *ui;
    QSqlDatabase sqlitedb;
    QString userId;

};
#endif // LOGINDIALOG_H
