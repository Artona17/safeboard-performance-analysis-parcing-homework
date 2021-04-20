import pandas as pd
from cmd import Cmd


class CpuInfo:
    def __init__(self, file, deleted_column='Idle (0)'):
        self.__cpu_info = pd.read_csv(file, decimal=',')
        self.__cpu_info = self.__cpu_info[self.__cpu_info.Process != deleted_column]

    def top(self, *filters, needed_data='Process', lim_processes=3, lim_libs=5):
        timestamp_in_interval = self.__cpu_info
        for f in filters:
            timestamp_in_interval = timestamp_in_interval[timestamp_in_interval[f.AttributeName].
                                                          apply(f.FilterPredicate)]

        three_most_frequent = timestamp_in_interval[needed_data].value_counts()[:lim_processes].index.tolist()
        top_3_top_5 = []
        for process in three_most_frequent:
            data_of_process = timestamp_in_interval[timestamp_in_interval[needed_data].apply(lambda x: x == process)]
            libraries = data_of_process['Module'].value_counts()[:lim_libs].index.tolist()
            top_3_top_5.append(libraries)
        return top_3_top_5, three_most_frequent


class FileIOInfo:
    def __init__(self, file):
        self.__file_io_info = pd.read_csv(file, decimal=',')

    def top(self, *filters, needed_data='Process', needed_sum='Duration (µs)', lim=3):
        processes_filtered_info = self.__file_io_info
        for f in filters:
            processes_filtered_info = processes_filtered_info[processes_filtered_info[f.AttributeName]
                                                              .apply(f.FilterPredicate)]

        return processes_filtered_info.groupby(needed_data)[needed_sum].sum().to_frame().reset_index() \
            .nlargest(lim, needed_sum)[needed_data].tolist()


class Filter:
    def __init__(self, name, filter_predicate):
        self.AttributeName = name
        self.FilterPredicate = filter_predicate


class Reporter:
    def __init__(self, file_out='out.log'):
        self.__file_out = file_out

    def cpu_report(self, top_5_libraries, processes, start, end):
        if isinstance(processes, list):
            processes_str = ', '.join(processes)
        else:
            return 'Ошибка! Передан не список процессов.'
        if isinstance(top_5_libraries, list):
            top_5_libraries = [', '.join(i) for i in top_5_libraries]
        else:
            return 'Ошибка! Передан не список библиотек.'
        with open(self.__file_out, 'a') as f:
            print(f'Для профиля cpu мы выяснили, что для ТОП-3 процессов по частоте встречаемости\n{processes_str}\n'
                  f'ТОП-5 библиотеками в интервале от {start} до {end} секунд являются соответственно:\n', file=f)
            for i in range(len(processes)):
                print(f'Для {processes[i]}: {top_5_libraries[i]}\n', file=f)
            print('=' * 20, file=f)

    def file_io_report(self, start, end, sums_sorted, needed_sum):
        sums_sorted = ', '.join(sums_sorted)
        if needed_sum == 'Duration (µs)':
            with open(self.__file_out, 'a') as f:
                print(f'Для профиля file_io мы выяснили, что ТОП-3 процессов с наибольшей\n'
                      f'длительностью записи в интервале от {start} до {end} секунд являются:\n'
                      f'{sums_sorted}', file=f)
                print('=' * 20, file=f)

        elif needed_sum == 'Size (B)':
            with open(self.__file_out, 'a') as f:
                print(f'Для профиля file_io мы выяснили, что ТОП-3 процессов с наибольшим количеством\n'
                      f'прочитанных байт файлов в "C:\\ProgramData" в интервале от'
                      f' {start} до {end} секунд являются:\n'
                      f'{sums_sorted}', file=f)
                print('=' * 20, file=f)


class CmdReading(Cmd):
    def do_get_params(self, args):
        args_list = args.split(' ')
        if len(args_list) == 0:
            return 'Передайте аргументы соответственно Readme.'
        open(args_list[1], 'w').close()
        sec_intervals = [int(i) for i in args_list[3:]]
        report = Reporter(file_out=args_list[1])
        if args_list[2] == 'cpu':
            cpu_info = CpuInfo(file=args_list[0])
            for i in range(1, len(sec_intervals), 2):
                args_for_report = cpu_info.top(Filter('TimeStamp (s)', lambda x: x >= sec_intervals[i - 1]),
                                               Filter('TimeStamp (s)', lambda x: x <= sec_intervals[i]))
                report.cpu_report(top_5_libraries=args_for_report[0], processes=args_for_report[1],
                                  start=sec_intervals[i - 1], end=sec_intervals[i])
        elif args_list[2] == 'file_io_1':
            file_io_info = FileIOInfo(file=args_list[0])
            needed_sum = 'Duration (µs)'
            for i in range(1, len(sec_intervals), 2):
                sums_sorted = file_io_info.top(Filter('Event Type', lambda x: x == 'Write'),
                                               Filter('Start (s)', lambda x: x >= sec_intervals[i - 1]),
                                               Filter('End (s)', lambda x: x <= sec_intervals[i]),
                                               needed_sum=needed_sum)
                report.file_io_report(start=sec_intervals[i - 1], end=sec_intervals[i], needed_sum=needed_sum,
                                      sums_sorted=sums_sorted)

        elif args_list[2] == 'file_io_2':
            file_io_info = FileIOInfo(file=args_list[0])
            needed_sum = 'Size (B)'
            for i in range(1, len(sec_intervals), 2):
                sums_sorted = file_io_info.top(Filter('Event Type', lambda x: x == 'Read'),
                                               Filter('Start (s)', lambda x: x >= sec_intervals[i - 1]),
                                               Filter('End (s)', lambda x: x <= sec_intervals[i]),
                                               Filter('File Path', lambda x: 'C:\\ProgramData' in x),
                                               needed_sum=needed_sum)
                report.file_io_report(start=sec_intervals[i - 1], end=sec_intervals[i], needed_sum=needed_sum,
                                      sums_sorted=sums_sorted)


def start_cmd():
    starter = CmdReading()
    starter.prompt = '>'
    starter.cmdloop('Введите команду get_params и аргументы согласно Readme')


if __name__ == '__main__':
    start_cmd()
