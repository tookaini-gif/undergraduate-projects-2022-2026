#ifndef HOSPITAL_CARE_H
#define HOSPITAL_CARE_H

#include <QDialog>

namespace Ui {
class hospital_care;
}

class hospital_care : public QDialog
{
    Q_OBJECT

public:
    explicit hospital_care(QWidget *parent = nullptr);
    ~hospital_care();

private slots:
    void on_backBtn_clicked();

private:
    Ui::hospital_care *ui;
};

#endif // HOSPITAL_CARE_H
