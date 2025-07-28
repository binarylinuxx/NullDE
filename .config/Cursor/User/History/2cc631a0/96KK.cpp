#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QFile>
#include <QDir>
#include <QDebug>

int main(int argc, char *argv[])
{
    QGuiApplication app(argc, argv);

    QQmlApplicationEngine engine;
    QString configPath = QDir::homePath() + "/.config/notifs/notifs.qml";
    if (!QFile::exists(configPath)) {
        qWarning() << "QML config not found at" << configPath;
        return 1;
    }
    engine.load(QUrl::fromLocalFile(configPath));
    if (engine.rootObjects().isEmpty())
        return -1;

    return app.exec();
}
