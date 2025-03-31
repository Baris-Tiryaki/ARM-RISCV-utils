default: dissassembly.txt

sample.o: sample.s
	riscv64-linux-gnu-gcc -c -march=rv32ifd -mabi=ilp32 sample.s -o sample.o

dissassembly.txt: sample.o
	riscv64-linux-gnu-objdump -d -M numeric,no-aliases sample.o | tee dissassembly.txt


run:
	qemu-system-riscv32 -nographic -machine sifive_e -kernel sample.o