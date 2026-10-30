#include "hospital_care.h"
#include "ui_hospital_care.h"

#include <QScreen>

hospital_care::hospital_care(QWidget *parent) :
    QDialog(parent),
    ui(new Ui::hospital_care)
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

hospital_care::~hospital_care()
{
    delete ui;
}

void hospital_care::on_backBtn_clicked()
{
    this->close();
}
