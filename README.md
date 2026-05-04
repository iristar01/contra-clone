# Contra Clone

一个魂斗罗风格的横向卷轴射击游戏，使用 Pygame 开发，支持浏览器直接游玩。

## 在线试玩

👉 [点击这里开始游戏](https://你的用户名.github.io/contra-clone/)

## 操作说明

| 按键 | 功能 |
|------|------|
| `A/D` 或 `←/→` | 左右移动 |
| `W` 或 `↑` | 向上瞄准 / 跳跃 |
| `S` 或 `↓` | 蹲下 |
| `Space` | 跳跃 |
| `J` 或 `Z` | 射击 |
| `Enter` | 开始 / 重新开始 |
| `Esc` | 暂停 |

## 游戏特色

- **4种武器**：普通、散射、速射、激光
- **4种敌人**：普通兵、重装兵、狙击手、奔跑者
- **道具系统**：击败敌人概率掉落武器升级或生命恢复
- **精美关卡**：4000px 横向滚动，多层平台与陷阱
- **粒子特效**：爆炸、枪口火焰、受击火花、屏幕震动
- **视差背景**：渐变天空、远山、飘动的云朵

## 本地运行

```bash
cd src
python3 main.py
```

## 技术栈

- Python 3
- Pygame
- Pygbag (WebAssembly 打包)

## 部署到 GitHub Pages

1. 在 GitHub 创建仓库 `contra-clone`
2. 推送代码到 main 分支
3. 进入 Settings → Pages → Source，选择 "Deploy from a branch"
4. Branch 选 `main`，文件夹选 `/docs`
5. 等待几分钟后即可访问 `https://你的用户名.github.io/contra-clone/`
