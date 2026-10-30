#include "docchats.h"
#include "ui_docChats.h"
#include "ChatItemWidget.h"

#include <QFileDialog>
#include <QMessageBox>
#include <QScreen>

docChats::docChats(QWidget *parent) :
    QDialog(parent),
    ui(new Ui::docChats)
{
    ui->setupUi(this);
    setupClient();

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

docChats::~docChats()
{
    sqlitedb.close();
    delete ui;
}

void docChats::on_pushButton_clicked()
{
     _client->connectToServer();
}

void docChats::setUserId(const QString &userId)
{
    this->userId = userId;
    //ui->doc_id->setText(userId);
    loadInfo();
}

void docChats::loadInfo()
{
    QSqlQuery query(sqlitedb);
    query.prepare("SELECT doc_name "
                  "FROM Doc_Info WHERE doc_id = :user_id");
    query.bindValue(":user_id", userId);

    if (query.exec() && query.next())
    {
        ui->label_userId->setText("@"+userId);
        this->userName = query.value(0).toString();
        ui->label_userName->setText(userName);
        ui->lnClientName->setText(userName);
    }
    else
    {
        QMessageBox::warning(this, "Error", "Failed to retrieve doctor information.");
    }

    query.clear();
    if (!query.prepare("SELECT picturePath FROM Doc_Info WHERE doc_name = :doc_name")) {
        //qDebug() << "Query preparation failed: " << query.lastError().text();
        return;
    }

    query.bindValue(":doc_name", userName);

    if (!query.exec()) {
        //qDebug() << "Failed to execute query: " << query.lastError().text();
        //QMessageBox::critical(this, "Query Error", "Failed to execute query: " + query.lastError().text());
        return;
    }

    if (query.next()) {
        QString picturePath = query.value(0).toString();
        QPixmap pix;

        if (!picturePath.isEmpty() && QFile::exists(picturePath)) {
            pix.load(picturePath);
        } else {
            pix.load("../icon1.png");  // Use the correct path for the default image
        }

        ui->icon->setPixmap(pix.scaled(100, 100, Qt::KeepAspectRatio));
    } else {
        QMessageBox::warning(this, "Not Found", "No profile picture found for this user.");
    }
}

void docChats::setupClient()
{
    _client = new ClientManager();

    connect(_client , &ClientManager::connected, [this](){
        ui->groupBox->setEnabled(true);
    });
    connect(_client, &ClientManager::disconnected, [this](){
        ui->groupBox->setEnabled(false);
    });
    connect(_client, &ClientManager::textMessageReceived, this, &docChats::dataReceived);
    connect(_client, &ClientManager::isTyping, this, &docChats::onTyping);
    connect(_client, &ClientManager::initReceivingFile, this, &docChats::onInitReceivingFile);
    connect(_client, &ClientManager::rejectReceivingFile, this, &docChats::onRejectReceivingFile);

    connect(ui->lnMessage, &QLineEdit::textChanged, _client, &ClientManager::sendIsTyping);
    connect(_client, &ClientManager::connectionACK, this, &docChats::onConnectionACK);
    connect(_client, &ClientManager::newClientConnectedToServer, this, &docChats::onNewClientConnectedToServer);
    connect(_client, &ClientManager::clientDisconnected, this, &docChats::onClientDisconnected);
    connect(_client, &ClientManager::clientNameChanged, this, &docChats::onClientNameChanged);

}

//void MainWindow::on_actionConnect_triggered()
//{
//    _client->connectToServer();
//}


void docChats::on_btnSend_clicked()
{
    auto message = ui->lnMessage->text().trimmed();
    _client->sendMessage(message, ui->cmbDestination->currentText());
//    ui->lstMessages->addItem(message);
    ui->lnMessage->setText("");
    ui->lnMessage->setFocus();

    auto chatWidget = new ChatItemWidget();
    chatWidget->setMessage(message, true);
    auto listWidgetItem = new QListWidgetItem();
    listWidgetItem->setSizeHint(QSize(0, 65));
    ui->lstMessages->addItem(listWidgetItem);
    ui->lstMessages->setItemWidget(listWidgetItem, chatWidget);
}

void docChats::dataReceived(QString message)
{
//    ui->lstMessages->addItem(data);
    auto chatWidget = new ChatItemWidget();
    chatWidget->setMessage(message);
    auto listWidgetItem = new QListWidgetItem();
    listWidgetItem->setSizeHint(QSize(0, 65));
    ui->lstMessages->addItem(listWidgetItem);
    listWidgetItem->setBackground(QColor(167, 255, 237));
    ui->lstMessages->setItemWidget(listWidgetItem, chatWidget);


}


void docChats::on_lnClientName_editingFinished()
{
    auto name = ui->lnClientName->text().trimmed();
    _client->sendName(name);
}


void docChats::on_cmbStatus_currentIndexChanged(int index)
{
    auto status = (ChatProtocol::Status)index;
    _client->sendStatus(status);
}

void docChats::onTyping()
{
    ui->status_label->setText("Server is typing...");
}


void docChats::on_btnSendFile_clicked()
{
    auto fileName = QFileDialog::getOpenFileName(this, "Select a file", "/home");
    _client->sendInitSendingFile(fileName);
}

void docChats::onRejectReceivingFile()
{
    QMessageBox::critical(this, "Sending File", "Operation rejected...");
}

void docChats::onInitReceivingFile(QString clientName, QString fileName, qint64 fileSize)
{
    auto message = QString("Client (%1) wants to send a file. Do you want to accept it?\nFile Name:%2\nFile Size: %3 bytes")
            .arg(clientName, fileName)
            .arg(fileSize);
    auto result = QMessageBox::question(this, "Receiving File", message);
    if (result == QMessageBox::Yes) {
        _client->sendAcceptFile();
    } else {
        _client->sendRejectFile();
    }

}

void docChats::onConnectionACK(QString myName, QStringList clientsName)
{
    ui->cmbDestination->clear();
    clientsName.prepend("All");
    clientsName.prepend("Server");
    foreach (auto client, clientsName) {
        ui->cmbDestination->addItem(client);
    }
    setWindowTitle(myName);
}

void docChats::onNewClientConnectedToServer(QString clienName)
{
    ui->cmbDestination->addItem(clienName);
}

void docChats::onClientNameChanged(QString prevName, QString clientName)
{
    for (int i = 0; i < ui->cmbDestination->count(); ++i) {
        if (ui->cmbDestination->itemText(i) == prevName) {
            ui->cmbDestination->setItemText(i, clientName);
            return;
        }
    }
}

void docChats::onClientDisconnected(QString clientName)
{
    for (int i = 0; i < ui->cmbDestination->count(); ++i) {
        if (ui->cmbDestination->itemText(i) == clientName) {
            ui->cmbDestination->removeItem(i);
            return;
        }
    }
}


void docChats::on_backBtn_clicked()
{
    this->close();
}
