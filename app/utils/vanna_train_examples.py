ddl = """
            CREATE TABLE IF NOT EXISTS user_health_risk_assessment (
                id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '记录ID',
                user_id VARCHAR(64) NOT NULL COMMENT '用户唯一标识',
                user_name VARCHAR(100) NOT NULL COMMENT '用户姓名',
                sex ENUM('男', '女', '其他') NOT NULL COMMENT '性别',
                age TINYINT UNSIGNED NOT NULL COMMENT '年龄',
                assessment_time DATETIME NOT NULL COMMENT '测评时间',
                assessment_count INT DEFAULT 1 COMMENT '测试次数',
                total_score TINYINT UNSIGNED NOT NULL COMMENT '总分',
                nutritional_impairment_score TINYINT UNSIGNED NOT NULL COMMENT '营养受损分',
                disease_severity_score TINYINT UNSIGNED NOT NULL COMMENT '疾病严重度分',
                age_score TINYINT UNSIGNED NOT NULL COMMENT '年龄分',
                assessment_basis TEXT COMMENT '评分依据说明',
                risk_level ENUM('无风险', '低风险', '中风险', '高风险') NOT NULL COMMENT '风险等级',
                bmi DECIMAL(4,2) COMMENT 'BMI指数',
                weight_change VARCHAR(100) COMMENT '体重变化情况',
                disease_condition TEXT COMMENT '疾病状况描述',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间'
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户健康风险测评记录表';
            """


# 训练业务文档
documentation = """
用户健康风险测评记录表包含NRS2002营养风险筛查的完整评分数据。
重要字段说明：
- total_score: 总分(0-7分)，分数越高风险越大
- nutritional_impairment_score: 营养受损评分(0-3分)
- disease_severity_score: 疾病严重度评分(0-3分)  
- age_score: 年龄评分(0-1分)，70岁以上为1分
- risk_level: 风险等级，根据总分自动计算
- assessment_count: 测评次数，反映用户测评频率

常用查询模式：
1. 查询高风险患者(低风险,则查询低风险,中风险则查询中风险)：WHERE risk_level = '高风险'
2. 按时间范围查询：WHERE assessment_time BETWEEN '开始时间' AND '结束时间'
3. 统计各风险等级人数：GROUP BY risk_level
4. 查询用户历史测评记录：WHERE user_id is not null
"""


# 训练示例SQL查询  #让模型“知道你希望它怎么写 SQL
example_sqls = [
    "SELECT user_name, age, total_score, risk_level FROM user_health_risk_assessment WHERE risk_level = '高风险' ORDER BY total_score DESC LIMIT 10",
    "SELECT risk_level, COUNT(*) as count FROM user_health_risk_assessment GROUP BY risk_level ORDER BY count DESC",
    "SELECT user_name, assessment_time, total_score FROM user_health_risk_assessment WHERE user_id = 'USER001' ORDER BY assessment_time DESC",
    "SELECT AVG(total_score) as avg_score, AVG(age) as avg_age FROM user_health_risk_assessment WHERE sex = '男'",
    "SELECT DATE(assessment_time) as date, COUNT(*) as daily_count FROM user_health_risk_assessment GROUP BY DATE(assessment_time) ORDER BY date DESC LIMIT 7"
]

def main(text: str) -> dict:
  start = text.find("</think>") + 8
  print(f"start:{start}")
  content_after_marker = text[start:]
  print(f"content_after_marker:{content_after_marker.strip()}")
  echarts_content = content_after_marker.strip()
  echarts_start = echarts_content.find("```echarts")
  if echarts_start != 0:
    echarts_start = echarts_content.find("```json")
  print(f"echarts_start:{echarts_start}")
  if echarts_start != -1:
    # 截取从"```echarts"开始到最后一个"```"结束的内容
    echarts_content = echarts_content[echarts_start+10:]
    print(f"filter chars from echarts_content:{echarts_content}")
    echarts_end = echarts_content.rfind("```")
    if echarts_end != -1:
      echarts_content = echarts_content[:echarts_end]
    print(f"filter:{echarts_content}")
  return {
    "result": echarts_content,
  }