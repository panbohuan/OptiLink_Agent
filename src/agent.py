import requests
import matplotlib.pyplot as plt
import pandas as pd
import os
import re
from datetime import datetime
from typing import Optional, List, Dict, Tuple
from matplotlib import font_manager
from src.prompts import SYSTEM_PROMPT
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS", "WenQuanYi Micro Hei"]
plt.rcParams["axes.unicode_minus"] = False

from config import (
    DEEPSEEK_API_KEY,
    BASE_URL,
    MODEL_NAME,
    REPORTS_DIR,
    MAX_HISTORY_LENGTH,
    DATA_PATH,
)

plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "Arial Unicode MS"]
plt.rcParams["axes.unicode_minus"] = False

CHART_KEYWORDS_MAP = {
    "饼图": [
        "比例",
        "占比",
        "分布",
        "男",
        "女",
        "性别",
        "年级",
        "频率",
        "场所",
        "动机",
        "渠道",
    ],
    "柱状图": ["频率", "次数", "每周", "每月", "生活费", "客单价", "金额"],
    "条形图": ["渠道", "种草", "排名", "对比", "最常"],
    "雷达图": ["时段", "偏好", "时间偏好", "时段偏好"],
}

QUESTION_KEYWORDS = {
    "性别": ["性别", "男", "女"],
    "年级": ["年级", "大一", "大二", "大三", "大四"],
    "生活费": ["生活费", "月均", "月", "可支配"],
    "夜间丰富度": ["丰富", "夜间餐饮", "选择"],
    "消费频率": ["频率", "每周", "每天", "次数"],
    "消费时段": ["时段", "20:00", "22:00", "深夜", "时间"],
    "消费场所": ["场所", "地点", "哪里", "地方"],
    "客单价": ["客单价", "10元", "20元", "35元", "50元", "花费", "消费金额"],
    "消费动机": ["动机", "为什么", "原因", "社交", "解压", "填饱"],
    "种草渠道": ["渠道", "抖音", "小红书", "美团", "种草", "发现"],
}

COLOR_SCHEME = {
    "primary": "#E74C3C",
    "secondary": "#3498DB",
    "tertiary": "#9B59B6",
    "quaternary": "#1ABC9C",
    "quinary": "#F39C12",
    "senary": "#E91E63",
}


class NightEconomyAgent:
    def __init__(self):
        self.api_key = DEEPSEEK_API_KEY
        self.model = MODEL_NAME
        self.reports_dir = REPORTS_DIR
        self.data_path = DATA_PATH
        self.conversation_history: List[Dict] = []
        self.max_history_length = MAX_HISTORY_LENGTH

        os.makedirs(self.reports_dir, exist_ok=True)

        self._setup_font()
        self._load_research_data()

    def _setup_font(self):
        font_paths = [
            "C:/Windows/Fonts/simhei.ttf",
            "C:/Windows/Fonts/msyh.ttc",
            "C:/Windows/Fonts/simsun.ttc",
        ]
        for font_path in font_paths:
            if os.path.exists(font_path):
                prop = font_manager.FontProperties(fname=font_path)
                plt.rcParams["font.family"] = prop.get_name()
                break

    def _load_research_data(self):
        self.stats = {}
        for f in os.listdir(self.data_path):
            if not f.endswith((".xlsx", ".xls")):
                continue
            df = pd.read_excel(os.path.join(self.data_path, f), header=None)
            for i in range(len(df)):
                if pd.isna(df.iloc[i, 0]):
                    continue
                row_str = str(df.iloc[i, 0]).strip()
                if row_str and (row_str[0].isdigit() or row_str.startswith('Q')):
                    labels, values = [], []
                    j = i + 2
                    while j < len(df):
                        if pd.isna(df.iloc[j, 0]) or str(df.iloc[j, 0]).startswith('本题'):
                            break
                        labels.append(str(df.iloc[j, 0]))
                        values.append(int(df.iloc[j, 1]) if pd.notna(df.iloc[j, 1]) else 0)
                        j += 1
                    key = self._get_key_from_text(row_str)
                    if key and labels:
                        self.stats[key] = {"labels": labels, "values": values, "title": row_str[:30]}

    def _get_key_from_text(self, text: str) -> str:
        kw_map = {
            "性别": "性别", "年级": "年级", "生活费": "生活费",
            "频率": "消费频率", "时段": "消费时段", "场所": "消费场所",
            "客单价": "客单价", "动机": "消费动机", "种草": "种草渠道"
        }
        for kw, key in kw_map.items():
            if kw in text:
                return key
        return None

    def _build_messages_with_history(self, message: str) -> List[Dict]:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for entry in self.conversation_history[-self.max_history_length :]:
            messages.append({"role": entry["role"], "content": entry["content"]})
        messages.append({"role": "user", "content": message})
        return messages

    def _select_chart_type(self, question: str) -> str:
        for chart_type, keywords in CHART_KEYWORDS_MAP.items():
            if any(kw in question for kw in keywords):
                return chart_type
        return "柱状图"

    def _match_question(self, question: str) -> Optional[str]:
        question_lower = question.lower()
        for topic, keywords in QUESTION_KEYWORDS.items():
            if any(kw.lower() in question_lower for kw in keywords):
                return topic
        return None

    def _extract_data_from_excel(self, topic: str) -> Dict:
        if topic in self.stats:
            return self.stats[topic]
        return {"labels": ["A", "B"], "values": [50, 50], "title": topic}

    def _generate_pie_chart(self, data: Dict, save_path: str):
        colors = list(COLOR_SCHEME.values())[: len(data["labels"])]

        plt.figure(figsize=(10, 8))
        plt.pie(
            data["values"],
            labels=data["labels"],
            autopct="%1.1f%%",
            colors=colors,
            startangle=90,
            explode=[0.02] * len(data["values"]),
        )
        plt.title(
            data.get("title", "数据分析"),
            fontsize=14,
            fontweight="bold",
            color="#333333",
        )
        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        plt.close()

    def _generate_bar_chart(self, data: Dict, save_path: str):
        colors = [
            COLOR_SCHEME["primary"] if i % 2 == 0 else COLOR_SCHEME["secondary"]
            for i in range(len(data["labels"]))
        ]

        plt.figure(figsize=(10, 6))
        bars = plt.bar(
            data["labels"],
            data["values"],
            color=colors,
            edgecolor="white",
            linewidth=1.5,
        )

        for bar, value in zip(bars, data["values"]):
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.5,
                str(value),
                ha="center",
                va="bottom",
                fontsize=10,
            )

        plt.title(
            data.get("title", "数据分析"),
            fontsize=14,
            fontweight="bold",
            color="#333333",
        )
        plt.xlabel("类别", fontsize=11)
        plt.ylabel("人数", fontsize=11)
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        plt.close()

    def _generate_horizontal_bar_chart(self, data: Dict, save_path: str):
        colors = [
            COLOR_SCHEME["primary"] if i % 2 == 0 else COLOR_SCHEME["secondary"]
            for i in range(len(data["labels"]))
        ]

        plt.figure(figsize=(10, 6))
        bars = plt.barh(
            data["labels"],
            data["values"],
            color=colors,
            edgecolor="white",
            linewidth=1.5,
        )

        for bar, value in zip(bars, data["values"]):
            plt.text(
                bar.get_width() + 0.5,
                bar.get_y() + bar.get_height() / 2,
                str(value),
                ha="left",
                va="center",
                fontsize=10,
            )

        plt.title(
            data.get("title", "数据分析"),
            fontsize=14,
            fontweight="bold",
            color="#333333",
        )
        plt.xlabel("人数", fontsize=11)
        plt.ylabel("渠道", fontsize=11)
        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        plt.close()

    def _generate_radar_chart(self, data: Dict, save_path: str):
        angles = [
            n / float(len(data["labels"])) * 2 * 3.1415926
            for n in range(len(data["labels"]))
        ]
        angles += angles[:1]
        values = data["values"] + data["values"][:1]

        plt.figure(figsize=(10, 8))
        ax = plt.subplot(111, polar=True)
        ax.plot(angles, values, "o-", linewidth=2, color=COLOR_SCHEME["primary"])
        ax.fill(angles, values, alpha=0.25, color=COLOR_SCHEME["secondary"])
        ax.set_thetagrids([a * 180 / 3.1415926 for a in angles[:-1]], data["labels"])
        plt.title(
            data.get("title", "数据分析"),
            fontsize=14,
            fontweight="bold",
            color="#333333",
            y=1.08,
        )
        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        plt.close()

    def chat(self, message: str) -> str:
        messages = self._build_messages_with_history(message)

        try:
            response = requests.post(
                f"{BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 2000,
                },
                timeout=30,
            )

            if response.status_code == 200:
                result = response.json()
                reply = result["choices"][0]["message"]["content"]

                self.conversation_history.append({"role": "user", "content": message})
                self.conversation_history.append(
                    {"role": "assistant", "content": reply}
                )

                if len(self.conversation_history) > self.max_history_length * 2:
                    self.conversation_history = self.conversation_history[
                        -self.max_history_length * 2 :
                    ]

                return reply
            else:
                return f"API 调用失败: {response.status_code} - {response.text}"

        except requests.exceptions.Timeout:
            return "请求超时，请检查网络连接后重试。"
        except requests.exceptions.RequestException as e:
            return f"网络请求异常: {str(e)}"
        except Exception as e:
            return f"发生错误: {str(e)}"

    def generate_chart(self, question: str) -> str:
        topic = self._match_question(question)
        chart_type = self._select_chart_type(question)
        data = self._extract_data_from_excel(topic or "通用")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_topic = re.sub(r"[^\w\u4e00-\u9fff]", "_", topic or "通用")
        filename = f"{safe_topic}_{chart_type}_{timestamp}.png"
        save_path = os.path.join(self.reports_dir, filename)

        try:
            if chart_type == "饼图":
                self._generate_pie_chart(data, save_path)
            elif chart_type == "条形图":
                self._generate_horizontal_bar_chart(data, save_path)
            elif chart_type == "雷达图":
                self._generate_radar_chart(data, save_path)
            else:
                self._generate_bar_chart(data, save_path)

            return save_path
        except Exception as e:
            return f"图表生成失败: {str(e)}"

    def chat_with_chart(self, message: str, need_chart: bool = False) -> dict:
        result = {"answer": self.chat(message), "chart_path": None}

        if need_chart:
            result["chart_path"] = self.generate_chart(message)

        return result

    def reset_history(self):
        self.conversation_history = []

    def get_stats(self) -> dict:
        chart_files = [f for f in os.listdir(self.reports_dir) if f.endswith(".png")]

        return {
            "model": self.model,
            "history_count": len(self.conversation_history) // 2,
            "charts_saved": len(chart_files),
            "reports_dir": self.reports_dir,
            "data_loaded": self.df is not None,
        }
