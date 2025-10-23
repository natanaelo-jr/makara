import os
import sys

str_header = """
#define _GNU_SOURCE
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdint.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/perf_event.h>
#include <asm/unistd.h>
"""

str_perffunc = """
static long
perf_event_open(struct perf_event_attr *hw_event, pid_t pid,
                int cpu, int group_fd, unsigned long flags)
{
    return syscall(__NR_perf_event_open, hw_event, pid, cpu, group_fd, flags);
}
"""

str_setup = """
    struct perf_event_attr pe;
    int fd_cycles, fd_instructions, fd_cache_ref, fd_cache_miss;
    uint64_t count_cycles, count_instructions, count_cache_ref, count_cache_miss;

    // configura evento base
    memset(&pe, 0, sizeof(struct perf_event_attr));
    pe.size = sizeof(struct perf_event_attr);
    pe.disabled = 1;         // começa desabilitado
    pe.exclude_kernel = 0;   // mede também kernel (0 = mede tudo)
    pe.exclude_hv = 1;       // ignora hypervisor

    // ---------------------
    // grupo principal: cpu cycles
    // ---------------------
    pe.type = PERF_TYPE_HARDWARE;
    pe.config = PERF_COUNT_HW_CPU_CYCLES;
    fd_cycles = perf_event_open(&pe, 0, -1, -1, 0);
    if (fd_cycles == -1) { perror("perf_event_open (cycles)"); exit(1); }

    // ---------------------
    // membro 1: instructions
    // ---------------------
    pe.config = PERF_COUNT_HW_INSTRUCTIONS;
    fd_instructions = perf_event_open(&pe, 0, -1, fd_cycles, 0);
    if (fd_instructions == -1) { perror("perf_event_open (instructions)"); exit(1); }

    // ---------------------
    // membro 2: cache references
    // ---------------------
    pe.config = PERF_COUNT_HW_CACHE_REFERENCES;
    fd_cache_ref = perf_event_open(&pe, 0, -1, fd_cycles, 0);
    if (fd_cache_ref == -1) { perror("perf_event_open (cache references)"); exit(1); }

    // ---------------------
    // membro 3: cache misses
    // ---------------------
    pe.config = PERF_COUNT_HW_CACHE_MISSES;
    fd_cache_miss = perf_event_open(&pe, 0, -1, fd_cycles, 0);
    if (fd_cache_miss == -1) { perror("perf_event_open (cache misses)"); exit(1); }
    """



str_start = """
    // ---------------------
    // Habilita o grupo
    // ---------------------
    ioctl(fd_cycles, PERF_EVENT_IOC_RESET, PERF_IOC_FLAG_GROUP);
    ioctl(fd_cycles, PERF_EVENT_IOC_ENABLE, PERF_IOC_FLAG_GROUP);

    // ======== Região medida ========
"""

str_stop = """
ioctl(fd_cycles, PERF_EVENT_IOC_DISABLE, PERF_IOC_FLAG_GROUP);
"""

str_results = """

    // ---------------------
    // Lê resultados
    // ---------------------
    read(fd_cycles, &count_cycles, sizeof(uint64_t));
    read(fd_instructions, &count_instructions, sizeof(uint64_t));
    read(fd_cache_ref, &count_cache_ref, sizeof(uint64_t));
    read(fd_cache_miss, &count_cache_miss, sizeof(uint64_t));

    // ---------------------
    // Mostra resultados
    // ---------------------
    printf("\n=== Resultados da região medida ===\n");
    printf("CPU cycles       : %lu\n", count_cycles);
    printf("Instructions     : %lu\n", count_instructions);
    printf("Cache references : %lu\n", count_cache_ref);
    printf("Cache misses     : %lu\n", count_cache_miss);

    if (count_cache_ref)
        printf("Taxa de miss     : %.2f%%\n",
               100.0 * (double)count_cache_miss / (double)count_cache_ref);

    // fecha os descritores
    close(fd_cycles);
    close(fd_instructions);
    close(fd_cache_ref);
    close(fd_cache_miss);
"""

def modifyFile(file):
    finalString = ""
    with open(file) as f:
        lines = f.readlines()

    inside_src_for = False
    brace_depth = 0
    injected = False

    for i, line in enumerate(lines):
        # substituições simples já feitas por você
        if line == "// includes\n":
            finalString += line
            finalString += str_header
            finalString += str_perffunc
            continue

        if line == "    int opt = atoi(argv[1]);\n":
            finalString += line
            finalString += str_setup
            continue

        # detectar o início do for que inicializa src
        if "for(" in line and "_len_src0" in line:
            inside_src_for = True
            brace_depth = 0

        if inside_src_for:
            # rastrear chaves para saber quando o for termina
            brace_depth += line.count("{")
            brace_depth -= line.count("}")

            # quando brace_depth voltar a 0, é o fim do for
            if brace_depth == 0:
                inside_src_for = False
                finalString += line

                finalString += str_start + "\n"
                injected = True
                continue
        if line == "free(d);\n":
            finalString += line
            finalString += str_stop

        if line == ""


        finalString += line

    if not injected:
        print(f"⚠️  Nenhum ponto de injeção encontrado em {file}")
    else:
        print(f"✅ Injeção feita em {file}")

    print(finalString)


def main():
    sources = os.listdir("Jotai")
    print(sources[1])
    # modifyFile(f"Jotai/{sources[1]}")
    


if __name__ == "__main__":
    main()
