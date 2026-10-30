#include "hospital_activity.h"
#include "ui_hospital_activity.h"

#include <QScreen>

hospital_activity::hospital_activity(QWidget *parent) :
    QDialog(parent),
    ui(new Ui::hospital_activity)
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

hospital_activity::~hospital_activity()
{
    delete ui;
}

void hospital_activity::on_backBtn_clicked()
{
    this->close();
}
