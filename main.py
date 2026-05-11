"""
优联智能决策助手 - 夜间经济分析系统
基于 DeepSeek 大模型 + 真实调研数据
功能: 智能对话 + 自动数据可视化
"""

import sys
import os
import subprocess
from datetime import datetime
from typing import Optional

from src.agent import NightEconomyAgent


class TerminalUI:
    """终端交互界面"""

    class Colors:
        HEADER = '\033[95m'
        BLUE = '\033[94m'
        CYAN = '\033[96m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        RED = '\033[91m'
        BOLD = '\033[1m'
        DIM = '\033[2m'
        RESET = '\033[0m'

    def __init__(self):
        self.agent: Optional[NightEconomyAgent] = None
        self.start_time = datetime.now()

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_banner(self):
        banner = f"""
{self.Colors.CYAN}{self.Colors.BOLD}{'=' * 60}{self.Colors.RESET}
{self.Colors.GREEN}{self.Colors.BOLD}   🌙 优联智能决策助手 - 夜间经济分析系统{self.Colors.RESET}
{self.Colors.DIM}{'=' * 60}{self.Colors.RESET}
{self.Colors.YELLOW}📊 基于优联团队市场调研报告 | 驱动: DeepSeek{self.Colors.RESET}
{self.Colors.BLUE}🎯 功能: AI对话 | 自动图表生成 | 数据洞察{self.Colors.RESET}
{self.Colors.DIM}{'=' * 60}{self.Colors.RESET}
        """
        print(banner)

    def print_help(self):
        help_text = f"""
{self.Colors.BOLD}📖 命令说明:{self.Colors.RESET}
  {self.Colors.GREEN}/chart [问题]{self.Colors.RESET}   - 生成图表（如: /chart 生活费分布）
  {self.Colors.GREEN}/stats{self.Colors.RESET}          - 查看系统状态
  {self.Colors.GREEN}/reset{self.Colors.RESET}          - 重置对话历史
  {self.Colors.GREEN}/help{self.Colors.RESET}           - 显示帮助
  {self.Colors.GREEN}/clear{self.Colors.RESET}          - 清屏
  {self.Colors.GREEN}/exit{self.Colors.RESET}           - 退出

{self.Colors.BOLD}💡 直接输入问题即可对话{self.Colors.RESET}
        """
        print(help_text)

    def print_status(self):
        stats = self.agent.get_stats()
        status_text = f"""
{self.Colors.BOLD}{'─' * 50}{self.Colors.RESET}
{self.Colors.CYAN}📊 系统状态{self.Colors.RESET}
{self.Colors.BOLD}{'─' * 50}{self.Colors.RESET}
  🧠 模型:     {stats.get('model', 'N/A')}
  💾 对话轮次: {stats.get('history_count', 0)}
  📈 图表数:   {stats.get('charts_saved', 0)}
  📁 数据:     {'✅ 已加载' if stats.get('data_loaded') else '⚠️ 未加载'}
{self.Colors.BOLD}{'─' * 50}{self.Colors.RESET}
        """
        print(status_text)

    def _open_file(self, path: str) -> bool:
        try:
            if os.name == 'nt':
                os.startfile(path)
            elif sys.platform == 'darwin':
                subprocess.call(('open', path))
            else:
                subprocess.call(('xdg-open', path))
            return True
        except Exception:
            return False

    def print_chart_result(self, chart_path: str):
        if chart_path and os.path.exists(chart_path):
            print(f"\n{self.Colors.GREEN}✅ 图表已生成{self.Colors.RESET}")
            print(f"{self.Colors.DIM}📁 {chart_path}{self.Colors.RESET}")
            if self._open_file(chart_path):
                print(f"{self.Colors.GREEN}🖼️ 已自动打开{self.Colors.RESET}")
        else:
            print(f"\n{self.Colors.RED}❌ 图表生成失败{self.Colors.RESET}")

    def print_response(self, text: str):
        print(f"\n{self.Colors.CYAN}{self.Colors.BOLD}🤖 优联助手:{self.Colors.RESET}")

        print(text)


    def run(self):
        self.clear_screen()
        self.print_banner()

        print(f"{self.Colors.DIM}⏳ 初始化...{self.Colors.RESET}")
        try:
            self.agent = NightEconomyAgent()
            print(f"{self.Colors.GREEN}✅ 初始化成功{self.Colors.RESET}\n")
        except Exception as e:
            print(f"{self.Colors.RED}❌ 初始化失败: {e}{self.Colors.RESET}")
            return

        self.print_help()

        while True:
            try:
                user_input = input(f"\n{self.Colors.GREEN}{self.Colors.BOLD}你:{self.Colors.RESET} ").strip()
                if not user_input:
                    continue

                cmd = user_input.lower()
                if cmd in ['/exit', '/quit', 'exit', 'quit']:
                    print(f"\n{self.Colors.GREEN}👋 再见{self.Colors.RESET}\n")
                    break
                elif cmd in ['/help', '/h', 'help']:
                    self.print_help()
                elif cmd in ['/clear', 'clear']:
                    self.clear_screen()
                    self.print_banner()
                elif cmd in ['/reset', 'reset']:
                    self.agent.reset_history()
                    print(f"{self.Colors.GREEN}✅ 对话已重置{self.Colors.RESET}")
                elif cmd in ['/stats', 'stats']:
                    self.print_status()
                elif user_input.startswith('/chart'):
                    question = user_input[6:].strip()
                    if not question:
                        print(f"{self.Colors.YELLOW}💡 用法: /chart 生活费分布{self.Colors.RESET}")
                        continue
                    print(f"{self.Colors.DIM}⏳ 生成图表中...{self.Colors.RESET}")
                    chart_path = self.agent.generate_chart(question)
                    self.print_chart_result(chart_path)
                else:
                    print(f"{self.Colors.DIM}⏳ 思考中...{self.Colors.RESET}")
                    response = self.agent.chat(user_input)
                    self.print_response(response)

            except KeyboardInterrupt:
                print(f"\n\n{self.Colors.GREEN}👋 再见{self.Colors.RESET}\n")
                break
            except Exception as e:
                print(f"{self.Colors.RED}❌ 错误: {e}{self.Colors.RESET}")


def main():
    TerminalUI().run()


if __name__ == "__main__":
    main()
