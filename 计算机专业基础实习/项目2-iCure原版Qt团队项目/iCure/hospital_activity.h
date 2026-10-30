#ifndef HOSPITAL_ACTIVITY_H
#define HOSPITAL_ACTIVITY_H

#include <QDialog>

namespace Ui {
class hospital_activity;
}

class hospital_activity : public QDialog
{
    Q_OBJECT

public:
    explicit hospital_activity(QWidget *parent = nullptr);
    ~hospital_activity();

private slots:
    void on_backBtn_clicked();

private:
    Ui::hospital_activity *ui;
};

#endif // HOSPITAL_ACTIVITY_H
