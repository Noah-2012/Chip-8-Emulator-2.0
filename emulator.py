import sys
import time
import os
import random
import argparse
import pygame
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from tkinter import filedialog

# Rich-Konsole initialisieren
console = Console()

class Start:

    def __init__(self):
        # Standardwerte
        self.tickrate = 500
        self.entrypoint = 0x200
        global tickrate, entrypoint

    def show_banner(self):
        console.print("  ██████╗██╗  ██╗██╗██████╗        █████╗       ███████╗███╗   ███╗██╗   ██╗██╗      █████╗ ████████╗ ██████╗ ██████╗ ", style="yellow")
        console.print(" ██╔════╝██║  ██║██║██╔══██╗      ██╔══██╗      ██╔════╝████╗ ████║██║   ██║██║     ██╔══██╗╚══██╔══╝██╔═══██╗██╔══██╗", style="yellow")
        console.print(" ██║     ███████║██║██████╔╝█████╗╚█████╔╝█████╗█████╗  ██╔████╔██║██║   ██║██║     ███████║   ██║   ██║   ██║██████╔╝", style="yellow")
        console.print(" ██║     ██╔══██║██║██╔═══╝ ╚════╝██╔══██╗╚════╝██╔══╝  ██║╚██╔╝██║██║   ██║██║     ██╔══██║   ██║   ██║   ██║██╔══██╗", style="yellow")
        console.print(" ╚██████╗██║  ██║██║██║           ╚█████╔╝      ███████╗██║ ╚═╝ ██║╚██████╔╝███████╗██║  ██║   ██║   ╚██████╔╝██║  ██║", style="yellow")
        console.print("  ╚═════╝╚═╝  ╚═╝╚═╝╚═╝            ╚════╝       ╚══════╝╚═╝     ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝", style="yellow")
 
        console.print("----------------------------------------", style="cyan")
        console.print("|        Welcome to the C8-Emulator    |", style="cyan")
        console.print("|        Version: 2.0                  |", style="cyan")
        console.print("|        Author : Noadsch12            |", style="cyan")
        console.print("|                                      |", style="cyan")
        console.print("|Type 'help' for a list of the commands|", style="cyan")
        console.print("----------------------------------------", style="cyan")


    ### und dann für die inputs ein kleines terminal.
    ### wenn dann am ende start emu oder start c8h eingegeben wird, startet der emulator
    ### vorher kann man noch schreiben so set tickrate(oder tr) <zahl> und set entrypoint(oder ep) <0x[entrypoint]>
    ### und dann(noch nicht geschrieben) villeicht, mache ich noch so argumente wie --no-gpu oder --max-fps <zahl> oder ähnliches.

    def show_help(self):
        console.print("\n[bold cyan]Verfügbare Befehle:[/bold cyan]")
        console.print("[yellow]  set tickrate <zahl>  [/yellow]- Setzt die Tickrate des Emulators (Standard: 500)")
        console.print("[yellow]  set entrypoint <0x...>  [/yellow]- Setzt die Entry-Point-Adresse (Standard: 0x200)")
        console.print("[yellow]  start emu  [/yellow]- Startet den Emulator")
        console.print("[yellow]  exit  [/yellow]- Beendet das Programm")

    prompt_string="""╔══C8-Emulator$$\n╚══════════════>>>"""

    def first_prompt(self):


        while True:
            command = Prompt.ask(f"[bold green]{self.prompt_string}[/bold green]").strip()

            if command.startswith("set tickrate") or command.startswith("set tr"):
                parts = command.split()
                if len(parts) == 3 and parts[2].isdigit():
                    self.tickrate = int(parts[2])
                    console.print(f"[bold yellow]Tickrate auf {self.tickrate} gesetzt.[/bold yellow]")
                else:
                    console.print("[bold red]Ungültige Eingabe! Benutze: set tickrate <zahl>[/bold red]")

            elif command.startswith("set entrypoint") or command.startswith("set ep"):
                parts = command.split()
                try:
                    if len(parts) == 3:
                        self.entrypoint = int(parts[2], 16)
                        console.print(f"[bold yellow]Entry-Point auf {hex(self.entrypoint)} gesetzt.[/bold yellow]")
                    else:
                        raise ValueError
                except ValueError:
                    console.print("[bold red]Ungültige Eingabe! Benutze: set entrypoint <0x...>[/bold red]")

            elif command.startswith("set file"):
                parts = command.split()
                if len(parts) == 3 and parts[2]:
                    self.filename = parts[2]
                    console.print(f"[bold yellow]Auszuführende Datei auf {self.filename} gesetzt[/bold yellow]")
                else:
                    console.print("[bold red]Ungültige Eingabe! Benutze: set file <file>[/bold red]")

            elif command == "help":
                self.show_help()

            elif command == "start emu" or command == "start c8h":
                console.print("[bold green]Starte den Emulator...[/bold green]")
                console.print(f"[bold yellow]Tickrate: {self.tickrate}[/bold yellow]")
                console.print(f"[bold yellow]Entry-Point: {hex(self.entrypoint)}[/bold yellow]")
                try:
                    console.print(f"[bold yellow]Datei: {self.filename}[/bold yellow]")
                except:
                    console.print("[bold red]Forgot to set File![/bold red]")
                break  # Hier würde der Emulator starten


            elif command == "exit":
                console.print("[bold red]Beende das Programm vollständig...[/bold red]")
                sys.exit()

            else:
                console.print("[bold red]Unbekannter Befehl! Tippe 'help' für eine Liste der Befehle.[/bold red]")


class Chip8:
    def __init__(self, start_instance):
        self.memory = [0] * 4096
        self.V = [0] * 16
        self.I = 0
        self.pc = start_instance.entrypoint
        self.stack = []
        self.display = [0] * (64 * 32)
        self.delay_timer = 0
        self.sound_timer = 0
        self.keypad = [0] * 16
        self.load_fontset()
        self.draw_flag = False

    def load_fontset(self):
        # 4x5 Sprites für die Zeichen 0-F
        fontset = [
            # 0-9, A-F
            0xF0, 0x90, 0x90, 0x90, 0xF0,  # 0
            0x20, 0x60, 0x20, 0x20, 0x70,  # 1
            0xF0, 0x10, 0xF0, 0x80, 0xF0,  # 2
            0xF0, 0x10, 0xF0, 0x10, 0xF0,  # 3
            0x90, 0x90, 0xF0, 0x10, 0x10,  # 4
            0xF0, 0x80, 0xF0, 0x10, 0xF0,  # 5
            0xF0, 0x80, 0xF0, 0x90, 0xF0,  # 6
            0xF0, 0x10, 0x20, 0x40, 0x40,  # 7
            0xF0, 0x90, 0xF0, 0x90, 0xF0,  # 8
            0xF0, 0x90, 0xF0, 0x10, 0xF0,  # 9
            0xF0, 0x90, 0xF0, 0x90, 0x90,  # A
            0xF0, 0x80, 0xF0, 0x80, 0xF0,  # B
            0xF0, 0x80, 0xF0, 0x80, 0x80,  # C
            0xF0, 0x90, 0x90, 0x90, 0xF0,  # D
            0xF0, 0x80, 0xF0, 0x80, 0x80,  # E
            0xF0, 0x90, 0xF0, 0x10, 0x10   # F
        ]
        self.memory[:len(fontset)] = fontset

    def load_rom(self, rom_path):
        try:
            with open(rom_path, "rb") as f:
                rom = f.read()
            console.print(f"Geladene ROM-Größe: {len(rom)} Bytes", style="yellow")
            for i in range(len(rom)):
                self.memory[0x200 + i] = rom[i]
        except FileNotFoundError:
            print("Fehler: ROM-Datei nicht gefunden!")
            sys.exit(1)

    def fetch_opcode(self):
        return (self.memory[self.pc] << 8) | self.memory[self.pc + 1]

    def execute_opcode(self, opcode):
        self.pc += 2
        first_nibble = opcode & 0xF000
        x = (opcode & 0x0F00) >> 8
        y = (opcode & 0x00F0) >> 4
        n = opcode & 0x000F
        nn = opcode & 0x00FF
        nnn = opcode & 0x0FFF

        self.opcode_name = ""
        self.handle_d_opcode(opcode)
        
         # Wenn der Opcode bereits verarbeitet wurde (handle_d_opcode)
        if self.opcode_name != "":
            return

        # Mapping von Opcodes auf Methoden und deren Namen
        opcode_map = {
            0x00E0: ("CLS", self.clear_display),  # Clear Display
            0x00EE: ("RET", self.return_subroutine),  # Return from Subroutine
            0x2000: (f"CALL {hex(self.pc)}", self.call_subroutine),  # Call Subroutine
            0xF007: (f"LD V{x}, DT", self.get_delay_timer),  # LD Vx, DT
            0xF015: (f"LD DT, V{x}", self.set_delay_timer),  # LD DT, Vx
            0xF018: (f"LD ST, V{x}", self.set_sound_timer),  # LD ST, Vx
            0xF029: (f"LD F, V{x}", self.load_sprite),  # LD F, Vx
        }


        # Wenn der Opcode im Mapping existiert, rufe die entsprechende Methode auf
        if opcode in opcode_map:
            opcode_name, method = opcode_map[opcode]  # Tuple entpacken
            self.opcode_name = opcode_name  # Setze den Opcode-Namen
            method()  # Rufe die Methode auf

        # Spezifische Behandlung für andere Opcodes
        elif first_nibble == 0x0000:
            self.opcode_name = f"NOP"
        elif first_nibble == 0x1000:  # JUMP
            self.opcode_name = f"JP {nnn:03X}"
            self.pc = nnn
        elif first_nibble == 0x2000:  # CALL
            self.opcode_name = f"CALL {nnn:03X}"
            self.stack.append(self.pc)
            self.pc = nnn
        elif first_nibble == 0x3000:  # SE Vx, byte
            self.opcode_name = f"SE V{x}, {nn:02X}"
            if self.V[x] == nn:
                self.pc += 2
        elif first_nibble == 0x4000:  # SNE Vx, byte
            self.opcode_name = f"SNE V{x}, {nn:02X}"
            if self.V[x] != nn:
                self.pc += 2
        elif first_nibble == 0x5000:  # SE Vx, Vy
            self.opcode_name = f"SE V{x}, V{y}"
            if self.V[x] == self.V[y]:
                self.pc += 2  # Überspringe den nächsten Befehl, wenn Vx == Vy
        elif first_nibble == 0x6000:  # LD Vx, byte
            self.opcode_name = f"LD V{x}, {nn:02X}"
            self.V[x] = nn
        elif first_nibble == 0x7000:  # ADD Vx, byte
            self.opcode_name = f"ADD V{x}, {nn:02X}"
            self.V[x] = (self.V[x] + nn) & 0xFF
        elif first_nibble == 0x8000:
            if n == 0x0:  # LD Vx, Vy
                self.opcode_name = f"LD V{x}, V{y}"
                self.V[x] = self.V[y]
            elif n == 0x1:  # OR Vx, Vy
                self.opcode_name = f"OR V{x}, V{y}"
                self.V[x] |= self.V[y]
            elif n == 0x2:  # AND Vx, Vy
                self.opcode_name = f"AND V{x}, V{y}"
                self.V[x] &= self.V[y]
            elif n == 0x3:  # XOR Vx, Vy
                self.opcode_name = f"XOR V{x}, V{y}"
                self.V[x] ^= self.V[y]
            elif n == 0x4:  # ADD Vx, Vy
                self.opcode_name = f"ADD V{x}, V{y}"
                result = self.V[x] + self.V[y]
                self.V[0xF] = 1 if result > 0xFF else 0
                self.V[x] = result & 0xFF
            elif n == 0x5:  # SUB Vx, Vy
                self.opcode_name = f"SUB V{x}, V{y}"
                self.V[0xF] = 1 if self.V[x] > self.V[y] else 0
                self.V[x] -= self.V[y]
            elif n == 0x6:  # SHR Vx
                self.opcode_name = f"SHR V{x}"
                self.V[0xF] = self.V[x] & 0x1
                self.V[x] >>= 1
            elif n == 0x7:  # SUBN Vx, Vy
                self.opcode_name = f"SUBN V{x}, V{y}"
                self.V[0xF] = 1 if self.V[y] > self.V[x] else 0
                self.V[x] = self.V[y] - self.V[x]
            elif n == 0xE:  # SHL Vx
                self.opcode_name = f"SHL V{x}"
                self.V[0xF] = (self.V[x] >> 7) & 0x1
                self.V[x] <<= 1
        elif first_nibble == 0x9000:  # SNE Vx, Vy
            self.opcode_name = f"SNE V{x}, V{y}"
            if self.V[x] != self.V[y]:
                self.pc += 2  # Überspringe den nächsten Befehl, wenn Vx != Vy
        elif first_nibble == 0xA000:  # LD I, addr
            self.opcode_name = f"LD I, {nnn:03X}"
            self.I = nnn
        elif first_nibble == 0xE000:
            if nn == 0xA1:  # SKP Vx
                self.opcode_name = f"SKP V{x}"
                if self.keypad[self.V[x]] == 0:
                    self.pc += 2
            elif nn == 0x9E:  # SKNP Vx
                self.opcode_name = f"SKNP V{x}"
                if self.keypad[self.V[x]] != 0:
                    self.pc += 2
        elif first_nibble == 0xF000:
            if nn == 0x07:  # LD Vx, DT
                self.opcode_name = f"LD V{x}, DT"
                self.V[x] = self.delay_timer
            elif nn == 0x15:  # LD DT, Vx
                self.opcode_name = f"LD DT, V{x}"
                self.delay_timer = self.V[x]
            elif nn == 0x18:  # LD ST, Vx
                self.opcode_name = f"LD ST, V{x}"
                self.sound_timer = self.V[x]
            elif nn == 0x1E:  # ADD I, Vx
                self.opcode_name = f"ADD I, V{x}"
                self.I += self.V[x]
            elif nn == 0x29:  # LD F, Vx
                self.opcode_name = f"LD F, V{x}"
                self.I = self.V[x] * 5
            elif nn == 0x33:  # LD B, Vx
                self.opcode_name = f"LD B, V{x}"
                value = self.V[x]
                self.memory[self.I] = value // 100
                self.memory[self.I + 1] = (value // 10) % 10
                self.memory[self.I + 2] = value % 10
            elif nn == 0x55:  # LD [I], Vx
                self.opcode_name = f"LD [I], V{x}"
                for i in range(x + 1):
                    self.memory[self.I + i] = self.V[i]
            elif nn == 0x65:  # LD Vx, [I]
                self.opcode_name = f"LD V{x}, [I]"
                for i in range(x + 1):
                    self.V[i] = self.memory[self.I + i]
        elif first_nibble == 0xC000:  # RND Vx, byte
            self.opcode_name = f"RND V{x}, {nn:02X}"
            import random
            self.V[x] = random.randint(0, 255) & nn
        else:
            self.opcode_name = f"Nicht implementierter Opcode: {opcode:04X}"


    def clear_display(self):
        self.display = [0] * (64 * 32)
        self.draw_flag = True

    def return_subroutine(self):
        self.pc = self.stack.pop()

    def get_delay_timer(self):
        self.V[0] = self.delay_timer

    def set_delay_timer(self):
        self.delay_timer = self.V[0]

    def set_sound_timer(self):
        self.sound_timer = self.V[0]

    def load_sprite(self):
        self.I = self.V[0] * 5
        
    def call_subroutine(self, opcode):
        address = opcode & 0x0FFF  # Die untersten 12 Bits als Adresse extrahieren
        self.stack.append(self.pc)  # Speichere aktuelle Adresse auf dem Stack
        self.pc = address  # Springe zur neuen Adresse

    def draw_sprite(self, x, y, height):
        self.V[0xF] = 0  # Reset carry flag
        for row in range(height):
            pixel = self.memory[self.I + row]
            for col in range(8):
                if (pixel & (0x80 >> col)) != 0:
                    # Berechne die Position, aber stelle sicher, dass sie im Bildschirmbereich bleibt
                    draw_x = self.V[x] + col
                    draw_y = self.V[y] + row
                
                    # Überprüfen, ob die Position im Bildschirmbereich liegt
                    if draw_x >= 64 or draw_y >= 32:
                        continue  # Wenn außerhalb des Bildschirms, überspringen
                    
                    index = draw_y * 64 + draw_x
                    if self.display[index] == 1:
                        self.V[0xF] = 1  # Setze das "collision"-Flag, wenn das Pixel bereits gesetzt ist
                    self.display[index] ^= 1  # XOR für das Setzen und Löschen des Pixels
                
        self.draw_flag = True  # Setze das Flag für die Anzeige


    def handle_d_opcode(self, opcode):
        # Überprüfe, ob der Opcode mit 0xD000 beginnt (also 0xDxxx)
        if (opcode & 0xF000) != 0xD000:
            # Falls der Opcode nicht mit 0xD beginnt, tue nichts und verlasse die Methode
            return

        # Extrahiere die relevanten Werte aus dem Opcode
        x = (opcode & 0x0F00) >> 8
        y = (opcode & 0x00F0) >> 4
        n = opcode & 0x000F
        self.opcode_name = f"DRW V{x}, V{y}, {n:01X}"
    
        # Rufe die `draw_sprite` Methode auf
        self.draw_sprite(x, y, n)



    def update_timers(self):
        if self.delay_timer > 0:
            self.delay_timer -= 1
        if self.sound_timer > 0:
            self.sound_timer -= 1


def main():
    start = Start()
    start.show_banner()
    start.first_prompt()

    pygame.init()
    screen = pygame.display.set_mode((640, 320))
    clock = pygame.time.Clock()
    chip8 = Chip8(start)
    chip8.load_rom(start.filename)

    # Farben definieren
    text_color = (0, 205, 0)

    # Zustand der Pause und der letzten Step-Taste
    is_paused = False
    last_step_time = 0
    step_delay = 100  # 100 ms Verzögerung für Step
    step_requested = False  # Wird gesetzt, wenn die "S"-Taste gedrückt wird

    key_map = {
        pygame.K_1: 0x1,
        pygame.K_2: 0x2,
        pygame.K_3: 0x3,
        pygame.K_4: 0xC,
        pygame.K_q: 0x4,
        pygame.K_w: 0x5,
        pygame.K_e: 0x6,
        pygame.K_r: 0xD,
        pygame.K_a: 0x7,
        pygame.K_s: 0x8,
        pygame.K_d: 0x9,
        pygame.K_f: 0xE,
        pygame.K_z: 0xA,
        pygame.K_x: 0x0,
        pygame.K_c: 0xB,
        pygame.K_v: 0xF
    }



    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:   
                if event.key == pygame.K_l:
                    pygame.quit()
                    sys.exit()
                    
                if event.key in key_map: 
                    key = key_map[event.key]
                    chip8.keypad[key] = 1 

                if event.key == pygame.K_TAB:
                    pygame.quit()
                    if __name__ == "__main__":
                        main()


            if event.type == pygame.KEYUP:
                if event.key in key_map:  
                    key = key_map[event.key]
                    chip8.keypad[key] = 0  
                    
           
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:  # Leertaste - Play/Pause
                    is_paused = not is_paused
                elif event.key == pygame.K_s:  # 'S' - Step
                    # Stelle sicher, dass 100ms zwischen den "S"-Tastendrücken vergehen
                    current_time = pygame.time.get_ticks()
                    if current_time - last_step_time >= step_delay:
                        step_requested = True  # Setze Step an, um einen einzelnen Schritt auszuführen
                        last_step_time = current_time  # Aktualisiere den Zeitstempel für den letzten Step-Tastendruck

        # Wenn nicht pausiert, führe kontinuierlich Schritte aus
        if not is_paused:
            opcode = chip8.fetch_opcode()
            chip8.execute_opcode(opcode)
            chip8.update_timers()

            # Nur PC und I im Terminal ausgeben, wenn nicht pausiert
            if chip8.opcode_name == "":
                console.print(f"[green]PC: {chip8.pc:04X}[/green] | [green]I: {chip8.I:04X}[/green] | [red]OP: {chip8.opcode_name}[/red]")
            else:
                console.print(f"[green]PC: {chip8.pc:04X}[/green] | [green]I: {chip8.I:04X}[/green] | [green]OP: {chip8.opcode_name}[/green]")

        # Wenn pausiert, führe einen einzelnen Schritt aus, falls Step angefordert
        if is_paused and step_requested:
            opcode = chip8.fetch_opcode()
            chip8.execute_opcode(opcode)
            chip8.update_timers()

            # Nur PC und I im Terminal ausgeben, wenn im Step-Modus
            if chip8.opcode_name == "":
                console.print(f"[green]PC: {chip8.pc:04X}[/green] | [green]I: {chip8.I:04X}[/green] | [red]OP: {chip8.opcode_name}[/red]")
            else:
                console.print(f"[green]PC: {chip8.pc:04X}[/green] | [green]I: {chip8.I:04X}[/green] | [green]OP: {chip8.opcode_name}[/green]")

            step_requested = False  # Reset nach einem Schritt

        if chip8.draw_flag:
            screen.fill((0, 0, 170))
            for y in range(32):
                for x in range(64):
                    if chip8.display[y * 64 + x]:
                        pygame.draw.rect(screen, (170, 170, 255), (x * 10, y * 10, 10, 10))
            pygame.display.flip()
            chip8.draw_flag = False

        clock.tick(start.tickrate)

if __name__ == "__main__":
    main()