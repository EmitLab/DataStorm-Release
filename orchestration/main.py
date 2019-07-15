from orchestration_core import bootstrap
from orchestration_core import configure


def main():
    server_info = bootstrap.bootstrap_all()
    configure.configure_all(server_info)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
