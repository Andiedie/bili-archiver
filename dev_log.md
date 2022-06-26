# 开发日志

# TODO
- [x] 使用 cookie 调用 API
  - [x] 历史 API
  - [x] 收藏夹 API
  - [x] Up 主视频 API
  - [x] 投稿视频 API
- [x] 投稿视频下载
- [x] 消失视频兼容
- [x] 获取视频基本信息，存入 SQLite
- [x] 使用 aria2c 下载
- [x] 记录保存在本地 SQLite
- [x] 合并下载的音视频
- [x] 确定获取最高分辨率的下载地址
- [x] 存储消失的视频
- [x] 逐个下载
- [ ] 以 cid 为基础记录

# API
## 获取播放历史
```bash
curl --location --request GET 'https://api.bilibili.com/x/web-interface/history/cursor?max=49405519&view_at=1642785653&business=archive' \
--header 'cookie: SESSDATA={登录态
}'
```

## 获取收藏夹列表
```bash
curl --location --request GET 'https://api.bilibili.com/x/v3/fav/folder/created/list-all?up_mid={用户ID}' \
--header 'cookie: SESSDATA={登录态}'
```

## 获取收藏夹视频
```bash
curl --location --request GET 'https://api.bilibili.com/x/v3/fav/resource/list?media_id={收藏夹ID}&pn=2&ps=20' \
--header 'cookie: SESSDATA={登录态}'
```

## 获取 Up 主视频
```bash
curl --location --request GET 'https://api.bilibili.com/x/space/arc/search?mid={用户ID}&ps=30&pn=2' \
--header 'cookie: SESSDATA={登录态}'
```

## 获取视频基本信息
```bash
curl --location --request GET 'https://api.bilibili.com/x/web-interface/view?bvid={BV号}'
curl --location --request GET 'https://api.bilibili.com/x/web-interface/view?aid={AV号}'
```

## 获取视频分 P
```bash
curl --location --request GET 'https://api.bilibili.com/x/player/pagelist?bvid={BV号}'
curl --location --request GET 'https://api.bilibili.com/x/player/pagelist?aid={AV号}'
```

## 获取下载地址
```bash
curl --location --request GET 'https://api.bilibili.com/x/player/playurl?avid={AV号}&cid={CID}'
```
