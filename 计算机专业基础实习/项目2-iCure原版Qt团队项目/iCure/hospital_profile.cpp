#include "hospital_profile.h"
#include "ui_hospital_profile.h"

#include <QScreen>

hospital_profile::hospital_profile(QWidget *parent) :
    QDialog(parent),
    ui(new Ui::hospital_profile)
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
}

hospital_profile::~hospital_profile()
{
    delete ui;
}

void hospital_profile::on_backBtn_clicked()
{
    this->close();
}
