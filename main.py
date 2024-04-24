import ui
import RepositoryHandler


def main():
    """
    Main part of whole application
    :return: None
    """
    while True:
        link = ui.get_link()
        repository = RepositoryHandler.init_repository_handler(link)
        if repository is not None:
            break
    ui.print_results(repository.get_statistics())


if __name__ == '__main__':
    main()
