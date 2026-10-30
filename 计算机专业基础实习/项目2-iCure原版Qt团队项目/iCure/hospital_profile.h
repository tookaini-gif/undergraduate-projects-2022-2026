#ifndef HOSPITAL_PROFILE_H
#define HOSPITAL_PROFILE_H

#include <QDialog>

namespace Ui {
class hospital_profile;
}

class hospital_profile : public QDialog
{
    Q_OBJECT

public:
    explicit hospital_profile(QWidget *parent = nullptr);
    ~hospital_profile();

private slots:
    void on_backBtn_clicked();

private:
    Ui::hospital_profile *ui;
};

#endif // HOSPITAL_PROFILE_H
