import sys
from twisted.internet import reactor
from twisted.python.filepath import FilePath

if sys.platform.startswith("linux"):
    from twisted.internet import inotify

    def handle_modification(event):
        print("File modified:", event.pathname)

    def start_file_monitoring(path):
        notifier = inotify.INotify()
        notifier.startReading()

        # Register the modification event for each file in the directory recursively
        notifier.watch(
            path,
            callbacks=[handle_modification],
            mask=inotify.IN_WATCH_MASK,
            autoAdd=True,
            recursive=True,
        )

        reactor.run()

elif sys.platform.startswith("win"):
    from twisted.internet import task
    from twisted.internet import win32file
    import win32con

    def handle_modification(results):
        for action, file_name in results:
            if action == win32con.FILE_ACTION_MODIFIED:
                print("File modified:", file_name)

    def start_file_monitoring(directory):
        directory = directory.encode("utf-16le")
        handle = win32file.CreateFile(
            directory,
            win32file.GENERIC_READ,
            win32file.FILE_SHARE_READ | win32file.FILE_SHARE_WRITE,
            None,
            win32file.OPEN_EXISTING,
            win32file.FILE_FLAG_BACKUP_SEMANTICS,
            None
        )

        overlapped = win32file.OVERLAPPED()
        buffer_size = 8192  # 8 KB buffer size, you can adjust it as needed
        results = []
        win32file.ReadDirectoryChangesW(
            handle,
            buffer_size,
            True,
            win32con.FILE_NOTIFY_CHANGE_LAST_WRITE,
            overlapped,
            handle_modification,
            results
        )

        def on_monitoring_failed(failure):
            print("Failed to monitor directory:", failure.getErrorMessage())

        reactor.callLater(1, task.deferLater, reactor, 0, on_monitoring_failed, None)
        reactor.run()

elif sys.platform.startswith("darwin"):
    from twisted.internet import kqreactor

    def handle_modification(kq, path):
        print("File modified:", path)

    def start_file_monitoring(path):
        kq = kqreactor.KQueueReactor()
        kq.startReading()

        file_descriptor = path.open("rb")
        kq.reactor.addReader(kq.fileno(), handle_modification, kq, path)

        reactor.run()

else:
    print("Unsupported platform.")
    sys.exit(1)


if __name__ == "__main__":
    directory_path = "../Memory"
    directory_path = FilePath(directory_path)  # Convert to FilePath for better compatibility
    print(f'Now watching {directory_path.dirname()}/Memory for changes in file system.')
    # Start monitoring the directory recursively
    if sys.platform.startswith("linux"):
        start_file_monitoring(directory_path)
    elif sys.platform.startswith("win"):
        start_file_monitoring(directory_path.dirname())
    elif sys.platform.startswith("darwin"):
        start_file_monitoring(directory_path)
