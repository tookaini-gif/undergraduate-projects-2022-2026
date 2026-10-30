#ifndef PATCHATS_H
#define PATCHATS_H

#include <QDialog>
#include "ClientManager.h"
#include <QSqlDatabase>
#include <QSqlQuery>
#include <QDebug>

QT_BEGIN_NAMESPACE
namespace Ui {
class patChats;
}
QT_BEGIN_NAMESPACE

class patChats : public QDialog
{
    Q_OBJECT

public:
    explicit patChats(QWidget *parent = nullptr);
    ~patChats();

    void setUserId(const QString &userId);


private slots:
    void on_backBtn_clicked();
    void on_pushButton_clicked();
    void on_btnSend_clicked();
    void dataReceived(QString message);
    void on_lnClientName_editingFinished();
    void on_cmbStatus_currentIndexChanged(int index);
    void onTyping();
    void on_btnSendFile_clicked();
    void onRejectReceivingFile();
    void onInitReceivingFile(QString clientName, QString fileName, qint64 fileSize);

    void onConnectionACK(QString myName, QStringList clientsName);
    void onNewClientConnectedToServer(QString clienName);
    void onClientNameChanged(QString prevName, QString clientName);
    void onClientDisconnected(QString clientName);

private:
    Ui::patChats *ui;
    QString userId;
    QString userName;
    ClientManager *_client;
    QSqlDatabase sqlitedb;

    void setupClient();
    void loadInfo();
};

#endif // PATCHATS_H
