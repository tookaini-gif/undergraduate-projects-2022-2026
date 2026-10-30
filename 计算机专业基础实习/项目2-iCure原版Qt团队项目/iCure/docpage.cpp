#include "docpage.h"
#include "ui_docpage.h"
#include "docprofile.h"
#include "docappointments.h"
#include "docchats.h"
#include "docpatients.h"
#include "docgraph.h"
#include "logindialog.h"
#include "hospital_activity.h"
#include "hospital_care.h"
#include "hospital_profile.h"

#include <QTimer>
#include <QDateTime>
#include <QMessageBox>
#include <QPixmap>
#include <QIcon>
#include <QScreen>
#include <QFile>

QTranslator translator1;

docPage::docPage(QWidget *parent) :
    QWidget(parent),
    ui(new Ui::docPage)
{
    ui->setupUi(this);

    // set timer
    QTimer *timer2=new QTimer(this);
    connect(timer2,SIGNAL(timeout()),this,SLOT(showTime()));
    timer2->start();

    QDate dateLbl=QDate::currentDate();
    QString date_text=dateLbl.toString("dd / MM / yyyy");
    ui->dateLbl->setText(date_text);

    //connect(ui->closeBtn1, &QPushButton::clicked, this, &docPage::close);
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
}

docPage::~docPage()
{
    delete ui;
}


void docPage::showTime()
{
    QTime time=QTime::currentTime();
    QString time_text=time.toString("hh : mm : ss");
    if((time.second()%2)==0)
    {
        time_text[3] = ' ';
        time_text[8] = ' ';
    }
    ui->timeLbl->setText(time_text);
}

void docPage::setUserId(const QString &userId)
{
    this->userId = userId;
    loadInfo();
}

void docPage::loadInfo()
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
    }
    else
    {
        QMessageBox::warning(this, "Error", "Failed to retrieve doctor information.");
    }

    query.clear();
    if (!query.prepare("SELECT picturePath FROM Doc_Info WHERE doc_name = :doc_name")) {
        qDebug() << "Query preparation failed: " << query.lastError().text();
        return;
    }

    query.bindValue(":doc_name", userName);

    if (!query.exec()) {
        qDebug() << "Failed to execute query: " << query.lastError().text();
        QMessageBox::critical(this, "Query Error", "Failed to execute query: " + query.lastError().text());
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

void docPage::on_docProfile_btn_clicked()
{
    this->hide();
    docProfile docProfile_page;
    docProfile_page.setUserId(userId);
    docProfile_page.exec();
    this->show();
    loadInfo();
}

void docPage::on_docAppointment_btn_clicked()
{
    this->hide();
    docAppointments docAppointment_page;
    docAppointment_page.setUserId(userId);
    docAppointment_page.exec();
    this->show();
}

void docPage::on_closeBtn1_clicked()
{

    QMessageBox::StandardButton reply;
    reply = QMessageBox::question(this, "Logout Confirmation", "Are you sure you want to log out?",
                                  QMessageBox::Yes | QMessageBox::No);

    if (reply == QMessageBox::Yes) {
        this->close();  // Close the current page

        loginDialog *loginPage = new loginDialog();
        loginPage->show();  // Show the login dialog again
    }

}

void docPage::on_Notice_btn_clicked()
{
    this->hide();
    hospital_care hc_page;
    hc_page.setModal(true);;
    hc_page.exec();
    this->show();
}

void docPage::on_docChats_btn_clicked()
{
    this->hide();
    docChats docChats_page;
    docChats_page.setUserId(userId);
    docChats_page.exec();
    this->show();
}

void docPage::on_docPatients_btn_clicked()
{
    this->hide();
    docPatients docPatients_page;
    docPatients_page.setUserId(userId);
    docPatients_page.exec();
    this->show();
}

void docPage::on_docGraph_btn_clicked()
{
    this->hide();
    docGraph docGraph_page;
    //docGraph_page.setUserId(userId);
    docGraph_page.exec();
    this->show();
}

void docPage::on_About_btn_clicked()
{
    this->hide();
    hospital_profile hp_page;
    hp_page.setModal(true);;
    hp_page.exec();
    this->show();
}

void docPage::on_Activity_btn_clicked()
{
    this->hide();
    hospital_activity ha_page;
    ha_page.setModal(true);;
    ha_page.exec();
    this->show();
}

void docPage::on_EN_clicked()
{
    translator1.load(":/new/znen/doctor_service_en_UK.qm");
    qApp->removeTranslator(&translator1); // 先移除旧的翻译器
    qApp->installTranslator(&translator1); // 然后安装新的翻译器

     ui->docProfile_btn->setText(tr("Profile"));
     ui->docChats_btn->setText(tr("Chats"));
     ui->docGraph_btn->setText(tr("Graph"));
     ui->docAppointment_btn->setText(tr("Appointment"));
     ui->docPatients_btn->setText(tr("Patients"));
     ui->label_3->setText(tr("Your Heath, Our Priority"));
     ui->About_btn->setText(tr("About Us"));
     ui->Activity_btn->setText(tr("Activity"));
}

void docPage::on_CN_clicked()
{
    translator1.load(":/new/znen/doctor_service_zh_CN.qm");
    qApp->removeTranslator(&translator1); // 先移除旧的翻译器
    qApp->installTranslator(&translator1); // 然后安装新的翻译器

     ui->docProfile_btn->setText(tr("个人信息"));
     ui->docChats_btn->setText(tr("聊天"));
     ui->docGraph_btn->setText(tr("图表"));
     ui->docAppointment_btn->setText(tr("预约"));
     ui->docPatients_btn->setText(tr("患者信息"));
     ui->label_3->setText(tr("您的健康，我们的首要任务"));
     ui->About_btn->setText(tr("关于我们"));
     ui->Activity_btn->setText(tr("活动"));
}
