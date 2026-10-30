#ifndef CHATMANAGER_H
#define CHATMANAGER_H

#include <QObject>

class ChatManager : public QObject
{
    Q_OBJECT
public:
    explicit ChatManager(QObject *parent = nullptr);

signals:

};

#endif // CHATMANAGER_H
