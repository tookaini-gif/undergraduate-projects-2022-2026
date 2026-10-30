#include "logindialog.h"

#include <QApplication>

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);
    loginDialog w;

    w.show();
    return a.exec();

}
