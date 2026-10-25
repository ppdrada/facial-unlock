import sys

if __name__ == "__main__":
    if "--check" in sys.argv:
        # modo sem janela, chamado pela tela de bloqueio
        from unlock_face import check

        sys.exit(check())

    from home import HomeScreen

    HomeScreen().run()
