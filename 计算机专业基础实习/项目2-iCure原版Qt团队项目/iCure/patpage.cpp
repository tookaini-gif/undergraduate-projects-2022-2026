#include "patpage.h"
#include "ui_patpage.h"
#include "patappointments.h"
#include "patprofile.h"
#include "patchats.h"
#include "pathealth.h"
#include "logindialog.h"
#include "hospital_activity.h"
#include "hospital_care.h"
#include "hospital_profile.h"

#include<QTimer>
#include<QDateTime>
#include <QMessageBox>
#include <QScreen>
#include <QFile>

QTranslator translator;

patPage::patPage(QWidget *parent) :
    QWidget(parent),
    ui(new Ui::patPage)
{
    ui->setupUi(this);

    // set timer
    QTimer *timer2=new QTimer(this);
    connect(timer2,SIGNAL(timeout()),this,SLOT(showTime()));
    timer2->start();

    QDate dateLbl=QDate::currentDate();
    QString date_text=dateLbl.toString("dd / MM / yyyy");
    ui->dateLbl->setText(date_text);

    sqlitedb = QSqlDatabase::addDatabase("QSQLITE");
    sqlitedb.setDatabaseName("icure_demo.sqlite");

    if (!sqlitedb.open()) {
        QMessageBox::warning(this, "Error", "Failed to open the database.");
    }

    //connect(ui->closeBtn1, &QPushButton::clicked, this, &patPage::close);
    setWindowFlag(Qt::FramelessWindowHint);
    setAttribute(Qt::WA_TranslucentBackground, true);

    // Center the window on the screen using QScreen
    QScreen *screen = QGuiApplication::primaryScreen();
    QRect screenGeometry = screen->geometry();
    int x = (screenGeometry.width() - this->width()) / 2;
    int y = (screenGeometry.height() - this->height()) / 2;
    this->move(x, y);
}

patPage::~patPage()
{
    sqlitedb.close();
    delete ui;
}

void patPage::showTime()
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

void patPage::setUserId(const QString &userId)
{
    this->userId = userId;
    //ui->label_userId->setText(userId);
    loadInfo();
}

void patPage::loadInfo()
{
    QSqlQuery query(sqlitedb);
    query.prepare("SELECT pat_name "
                  "FROM Pat_Info WHERE pat_id = :user_id");
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
    if (!query.prepare("SELECT picturePath FROM Pat_Info WHERE pat_name = :pat_name")) {
        qDebug() << "Query preparation failed: " << query.lastError().text();
        return;
    }

    query.bindValue(":pat_name", userName);

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

void patPage::on_patProfile_btn_clicked()
{
    this->hide();
    patProfile patProfile_page;
    patProfile_page.setUserId(userId);
    patProfile_page.exec();
    this->show();
    loadInfo();
}

void patPage::on_patAppointment_btn_clicked()
{
    this->hide();
    patAppointments patAppointment_page;
    patAppointment_page.setUserInfo(userId);
    patAppointment_page.exec();
    this->show();
}


void patPage::on_pushChat_btn_clicked()
{
    this->hide();
    patChats docChats_page;
    docChats_page.setUserId(userId);
    docChats_page.exec();
    this->show();

}

void patPage::on_patHealthAssesment_btn_clicked()
{
    this->hide();
    patHealth patHealth_page;
    patHealth_page.setUserId(userId);
    patHealth_page.exec();
    this->show();
}

void patPage::on_closeBtn1_clicked()
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



void patPage::on_hospital_care_clicked()
{
    this->hide();
    hospital_care hc_page;
    hc_page.setModal(true);;
    hc_page.exec();
    this->show();
}

void patPage::on_hospital_profile_clicked()
{
    this->hide();
    hospital_profile hp_page;
    hp_page.setModal(true);;
    hp_page.exec();
    this->show();
}

void patPage::on_hospital_activity_clicked()
{
    this->hide();
    hospital_activity ha_page;
    ha_page.setModal(true);;
    ha_page.exec();
    this->show();
}


void patPage::on_EN_clicked()
{
    translator.load(":/new/znen/doctor_service_en_UK.qm");
    qApp->removeTranslator(&translator); // 先移除旧的翻译器
    qApp->installTranslator(&translator); // 然后安装新的翻译器

     ui->patProfile_btn->setText(tr("Profile"));
     ui->pushChat_btn->setText(tr("Chats"));
     ui->patHealthAssesment_btn->setText(tr("Health Assesment"));
     ui->patAppointment_btn->setText(tr("Appointment"));
     ui->label_3->setText(tr("Your Heath, Our Priority"));
     ui->label_4->setText(tr("About Us"));
     ui->label_5->setText(tr("Activity"));
}

void patPage::on_CN_clicked()
{
    translator.load(":/new/znen/doctor_service_zh_CN.qm");
    qApp->removeTranslator(&translator); // 先移除旧的翻译器
    qApp->installTranslator(&translator); // 然后安装新的翻译器

     ui->patProfile_btn->setText(tr("个人信息"));
     ui->pushChat_btn->setText(tr("聊天"));
     ui->patHealthAssesment_btn->setText(tr("健康评估"));
     ui->patAppointment_btn->setText(tr("预约"));
     ui->label_3->setText(tr("您的健康，我们的首要任务"));
     ui->label_4->setText(tr("关于我们"));
     ui->label_5->setText(tr("活动"));
}
