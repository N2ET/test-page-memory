import mem_log
mem_log.init_config()
mem_log.start()
input('input anything to terminal:')
mem_log.stop()
mem_log.save_data()
