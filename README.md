# ServerSafe Helper 

## Introduction

**ServerSafe Helper** 是一款面向 Linux 系统的安全检查与修复工具，采用模块化架构设计，支持账户安全、SSH 配置、防火墙策略、日志审计、补丁管理、端口扫描等关键安全场景的检测与修复。

工具内置 dryrun 模式与回滚机制，确保批量修复过程中兼顾安全性与可控性。项目以**结构清晰、逻辑可控、运维友好**为设计原则，适合作为自动化合规修复框架的基础组件。

---

## Structure

```bash
.
├── backup/                # 修复前自动备份目录
├── config/                # 配置文件存放目录
│   └── config.py
├── json/                  # 扫描与修复结果输出（JSON 格式）
│   ├── account.json
│   └── detect_result.json
├── log/                   # 执行日志存储目录
│   └── 2025-06-15.log
├── main.py                # 程序入口文件
├── modules/               # 功能模块核心逻辑
│   ├── account/           # 账户安全模块
│   │   ├── dryrun.py      # 账户安全检测逻辑
│   │   ├── fix.py         # 账户安全修复逻辑
│   │   └── score.py       # 账户安全评分逻辑
│   ├── firewall/          # 防火墙模块
│   │   ├── dryrun.py
│   │   ├── fix.py
│   │   └── score.py
│   ├── logaudit/          # 日志审计模块
│   │   ├── dryrun.py
│   │   ├── fix.py
│   │   └── score.py
│   ├── patch/             # 补丁管理模块
│   │   ├── dryrun.py
│   │   ├── fix.py
│   │   └── score.py
│   ├── portscan/          # 端口扫描模块
│   │   ├── dryrun.py
│   │   ├── fix.py
│   │   └── score.py
│   ├── ssh/               # SSH 配置模块
│   │   ├── dryrun.py
│   │   ├── fix.py
│   │   └── score.py
│   ├── all_dryrun.py      # 各模块预检统一调用逻辑
│   ├── all_fix.py         # 各模块修复统一调用逻辑
│   ├── all_rollback.py    # 各模块回滚统一调用逻辑
│   ├── all_scan.py        # 各模块扫描统一调用逻辑
│   ├── cli.py             # 命令行参数解析与入口
│   └── operation.py       # 全局任务调度逻辑
├── utils/                 # 公共工具库
│   ├── backup_rollback.py # 备份与回滚工具
│   ├── detect_os.py       # 操作系统环境检测
│   └── log.py             # 日志打印工具
└── README.md              # 项目说明文档

```

## Features
```
备份回滚系统：所有修复动作执行前自动备份，支持失败回滚。

日志记录系统：统一日志模块输出详细执行信息，便于问题溯源。

幂等性控制：所有修复逻辑具备幂等性，避免重复执行副作用。

模块解耦架构：检测、修复、评分逻辑完全分离，便于扩展与维护。

```

## Usage
```
通过 main.py 启动整体逻辑，支持命令行参数：

参数	功能说明
--help/-h	显示帮助信息
--scan	执行安全检查
--dryrun	模拟执行
--fix	执行自动修复
--rollback	执行修复回滚
```

## Implementation

### 账户安全（account）
| 检查项 | 具体执行逻辑 |
|--------|--------------|
| 检查空密码 | 1.用 awk 命令，指定分隔符 -F:，读取 /etc/shadow 文件（/etc/下的敏感配置文件只有root可读，用os.geteuid() != 0判断，如果uid不为0则退出程序）检查第二列（即密码字段）是否为空（$2 == ""），如果为空，输出该行的用户名字段，将结果存储在 users 列表里（方便存入日志，控制台输出，后续的对应修复）,不为空则检查通过。 |
| 检查是否存在uid为0但用户名非root的用户 | 2.用 awk 命令，指定分隔符 -F:，读取 /etc/passwd 文件，检查第三列（UID 字段）是否等于 0。排除出用户名为 "root" ($1 != "root")的uid，输出其他 UID 为 0 的用户名,不存在则检查通过。 |
| 检查高危 UID 配置 | 3.定义高权限组列表：sudo，wheel，admin，用for循环遍历列表里的每个组，执行命令getent group <group>查询该组以及其成员是否存在；如果命令执行正常（returncode == 0），输出不为空（stdout.strip())，就按冒号 : 分割命令输出，并把结果存储为parts列表，取第四部分parts[3]（<group>的全部成员用户名），用逗号分隔，得到单个的用户名，最后用for循环逐个分析用户名，跳过用户名为空格的和用 getpass.getuser()得到的当前用户名，其余用户均视为风险用户，加入risky_users，统一写成json格式方便存储,risky_users不存在则检查通过。 |

### SSH 安全（ssh）
| 检查项 | 具体执行逻辑 |
|--------|--------------|
| 检查 SSH 是否禁止 root 登录 | 1，打开并读取 /etc/ssh/sshd_config 文件，将读取到的config文件转为小写(sshd_config 文件中的配置项并不区分大小写,强制转小写方便后续匹配),检查文件内容中是否存在 "permitrootlogin no"，存在则检查通过。 |
| 检测 SSH 是否禁止空密码登录 | 2,同样打开并且读取/etc/ssh/sshd_config文件，转为小写，搜索 "permitemptypasswords no"，存在则检查通过。 |
| 检测 SSH 最大认证失败尝试次数是否合理 | 3，设置默认最大认证失败尝试次数max_auth 为6次(（如果后续的检查找不到配置文件，则认为系统沿用了最大认证次数为默认值 6，以默认次数为6次来进行判定）)，按行读取sshd_config配置文件，逐行检查是否有 maxauthtries 开头的行,存在则按空白字符分割当前行,结果储存为字符串列表 parts,如果分割结果是否至少包含两个元素（有配置项maxauthtries和数值），存下列表的第二个元素（SSH 尝试次数）为max_auth，如果max_auth <= 4，检查结果存为合理的配置，检查通过。大于4，记录为不合理的配置。 |

### 防火墙安全（firewall）
| 检查项 | 具体执行逻辑 |
|--------|--------------|
| 防火墙是否安装并启用 | 先检查是否为 root 权限（用 os.geteuid()，非 0 直接退出）,再使用导入的detect_os_family文件，根据系统文件判断系统属于 RedHat 系或 Debian 系：a.RedHat 系防火墙检查逻辑：1.检查防火墙是否在运行：使用subprocess运行rpm -q firewalld，检查firewalld 安装状态，再运行systemctl is-active firewalld，检查firewalld 运行状态，如果返回值为0，则正在运行，检查通过。b.Debian 系防火墙检查逻辑：1.运行dpkg -s ufw查看ufw安装状态，再运行ufw status检查运行状态，如果返回值为0且运行结果含有"Status: active"，则检查通过。 |
| 默认策略是否严谨（deny 或 block/drop） | a.RedHat 系：2.运行firewall-cmd --get-default-zone，检查默认区域安全性，如果返回值为0且运行结果含有"drop"和"block"，则默认策略为拒绝，检查通过。b.Debian 系：2.运行ufw status verbose，看是否为deny，是则检查通过。 |
| 日志记录是否开启 | a.RedHat 系：3.运行firewall-cmd --get-log-denied，检查日志记录状态，如果返回值为0且运行结果不含"off",则检查通过。b.Debian 系：3.运行ufw status verbose，如果结果为on，则日志检查通过。 |

### 日志审计（logaudit）
| 检查项 | 具体执行逻辑 |
|--------|--------------|
| 检测auditd 安装状态 | 1，检查是否为 root 权限（用 os.geteuid()，非 0 直接退出），用subproces执行 which auditd 检查 日志审计核心组件auditd 是否已安装并持久启用，若已经安装，则检查通过。 |
| 关键文件审计规则 | 2.遍历 /etc/audit/rules.d/*.rules 目录下的所有规则文件，读取并去掉注释和空行，整理出所有已有规则集合，对比是否包含对以下三个敏感文件的监控：/etc/passwd，/etc/shadow，/var/log/secure，若三项规则全部存在，则检查通过。 |
| 日志轮转配置的检测 | 3.遍历 /etc/logrotate.d/ 目录下所有配置文件，检查是否存在/var/log/audit/audit.log的轮转配置，存在则检查通过。 |

### 补丁管理（patch）
| 检查项 | 具体执行逻辑 |
|--------|--------------|
| 更新缓存是否存在 | 1.检查以下任一目录是否存在：/var/lib/apt/lists(Debian系更新缓存),/var/cache/dnf（Redhat系更新缓存）,/var/cache/yum(老版本RHEL/CentOS系更新缓存),只要任一存在则检查通过。 |
| 自动更新是否开启 | 2，使用导入的detect_os_family文件，根据系统文件判断系统属于 RedHat 系或 Debian 系,针对不同发行版检测配置文件内容：Debian系：读取 /etc/apt/apt.conf.d/20auto-upgrades。查找文件中是否包含字符 '1'（if '1' in content），RedHat系： 读取 /etc/dnf/automatic.conf。查找检查结果是否包含 apply_updates = yes（转小写后匹配）。 |
| 更新日志是否存在 | 3.检查以下任一日志文件是否存在：/var/log/apt/history.log（Debian系更新历史）,/var/log/dnf.log（RHEL8+）,/var/log/yum.log（RHEL7-）,如果存在，则检查通过。 |

### 端口扫描（portscan）
| 检查项 | 具体执行逻辑 |
|--------|--------------|
| 检测 SSH 是否监听范围是否过宽（0.0.0.0 或 [::]，即全网可访问） | 1，用subprocess执行ss -ltnp 命令，获取本机 TCP 监听端口与绑定地址，如果非 0，记录异常，遍历输出行： 只要有 0.0.0.0:22 或 [::]:22，判定为绑定公网，bound_public 变为True，否则检查通过。 |
| 检测 Telnet 服务是否启用 | 2，执行 systemctl is-enabled telnet.socket 命令，根据命令返回码 retcode 判断：如果retcode == 0，服务启用（Telnet 协议为明文传输协议，启用则存在高危通信劫持风险。），否则检查通过。 |
| 检测 FTP 服务是否已安装 | 3，执行 which vsftpd 命令（FTP 同样属于明文协议，暴露用户密码风险），判断输出内容（output）是否存在：若不存在，则检查通过。 |

## Roadmap
扫描的模块并没有涵盖整个，仅仅覆盖了六大基本安全模块，为了做到全面检查，后续会加上内核安全与参数（sysctl 参数、内核模块、核心防御机制，用到的典型工具有sysctl, modprobe, grsecurity），Web 服务与应用（Web 服务暴露面、应用组件漏洞，用到的典型工具为nikto, wpscan, sqlmap），加密与证书安全（TLS 配置、证书有效性，用到的典型工具有openssl s_client）

现代安全合规标准（如CIS）要求细致的系统安全检查,受目前所掌握的技术所限，每个检查板块只实现了基础的三个扫描项，每个板块待增加的检查项列出如下.

account: 账号锁定与禁用,避免废弃账号被滥用();，检查敏感文件的权限及所有者（防止权限滥用）.

ssh :空闲会话自动上锁(ClientAliveInterval),限制 SSH 可登录账户范围(AllowUsers),防止 SSH 被用作跳板(AllowAgentForwarding no)

firewall :入站规则粒度,不应暴露非必要端口(nmap);出站规则限制,防止恶意进程主动连接攻击者(iptables).接口绑定规则,防止意外暴露在公网接口(ss),

logaudit:启用内核 boot 参数 audit=1 ,开机强制进入审计模式;全面事件覆盖：账户、权限变更、执行、网络连接、身份认证等,防止绕过审计死角;审计日志权限完整性(audit.log 文件权限、属主是否只限 root、auditd)

patch:判断是否存在已知高危漏洞尚未修补(CVE 检查),补丁失败记录检测(查看 apt/dnf/yum 日志中的失败记录)

portscan:全系统 TCP/UDP 监听端口扫描，避免遗漏未知服务;异常服务检测;UDP 服务监听检测

## Notes
依赖 Python 3.10 环境。

部分检查与所有修复功能需 sudo 权限执行。

## Quick Start
```bash
# 执行扫描
（sudo）python3 main.py --scan

# 仅检测不修复
python3 main.py --dryrun

# 自动修复
sudo python3 main.py --fix

# 回滚上次修复
python3 main.py --rollback

```