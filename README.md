# c0s1nT  
Development of a Dark Web Leak Notification and OSINT Collection System  
![image](https://github.com/user-attachments/assets/7e5d924b-962c-48ce-9073-7e22c2df8b85)
![image](https://github.com/user-attachments/assets/aea96225-10af-4013-a82e-5c5c5d79459e)


디스코드봇은 db로 관리되어서 해당 코드로 아무것도 실행 안하셔도 됩니다  
예를들어  개인 봇을 만드실려면 아래 사항을 따라주세요.  
1.가상환경에서 main.py 실행  
2.공유폴더에 디렉토리 지정해서 저장  
3.로컬에서 tor.py 코드에 디스코드봇 초대 디스코드 디벨롭 사이트 접속 후 봇생성 후 토큰 발급 코드에 your token 부분에 토큰 입력, 서버 채널id, 채널 id  입력   
4.database2.py 코드 열람 하여 최초 db 입력하도록 실행   
5.디스코드 명령어 !t,!h~!h3 입력 자유롭게 사용  

가상환경 실행코드 (칼리 리눅스)  
= main.py (코드 일원화)  
- tor1.py  
- tor2.py  

디스코드 봇 -  
- database2.py : db main file  
- tormain.py : discord main bot file

---

목표 : 다크웹 유출 정보 알림 시스템 개발  
인원 : 3명  
역할 : 팀장(PM) / 크롤러 및 디스코드 봇 개발  
개발일정 : 2024.05.28~2024.06.11  
사용기술 : Vmware, Tor, Discord, Python  
프로젝트 요약 : 다크웹 유출 정보 알림 및  
OSINT 수집 시스템 알림 봇 개발  
Notion : [Team page](https://heavenly-sponge-d64.notion.site/3-18aa9083fe54412db7a75a1c22e855c4)  
실행영상 : [youtube](https://www.youtube.com/watch?v=CRGCGoviEV0)  
보고서 : [Google Drive](https://drive.google.com/file/d/1TlANg5VdX2b9OCp8iXmrVV9rvkmRB-eD/view)  
  
주요 기능 :  
다크웹 조사 및 접속 자동화 , 크롤러 및 데이터베이스 관리 자동화 시스템  
알림 시스템 구축, 디스코드 봇을 통한 실시간 다크웹 조회 tor 링크로 open 가능 기능 제작  
테스트 및 검증, 다크웹에서 데이터 확인 후 변경 사항 발생 시 변경사항 적용 테스트 구현  
디스코드 간단한 명령어를 통해 편의성 제공 (!t,!h~!h3 입력)  
GitHub 통합: 프로젝트 코드는 GitHub에 공개를 통해 커뮤니티의 기여  

개인 성과:  
디스코드 봇 개발  
3개 Deep web 사이트 크롤러 기능 삽입 및 데이터베이스 관리  
문제해결 및 개선사항 수정  
테스트 및 검증  
문서 작성 및 발표  
보고서 작성  
노션 팀 페이지 제작  
