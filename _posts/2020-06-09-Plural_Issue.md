---
layout: post
title: "[Plural Issue] Plural 이슈 해결 과정"
tags: [WordCloud Plural Issue]
---
> Word cloud 내부에 존재하던 Plural Issue를 해결하는 과정을 담은 문서입니다.
<hr>

우리 팀은 word cloud 프로젝트에서 흥미로운 이슈들이 무엇이 존재하는지 탐색했고, 그 중 우리가 해결할 수 있을 것같은 이슈를 발견하였다.

![Plural_Issue](https://user-images.githubusercontent.com/58473522/84213060-9feee180-aafa-11ea-85e4-7e696cbc3343.PNG)

[plural issue][Plural_Issue_page]는 영어에서 복수형태의 단어를 모두 단수형태로 일반화하는 기능에 문제가 있다는 이슈이다.

원 프로젝트는 plural(복수) 형태인 단어를 모두 singular(단수) 형태로 normalise하는 것으로 normalise_plurals=True로 설정하여 진행하는데, 
그렇게 하는 경우 ‘s’로 끝나는 ‘virus’같은 단어가 복수형태와 구분이 되지 않아서 ‘viru’로 처리되는 등 의도와 다르게 ‘s’가 삭제되는 버그가 발생하는 것을 확인할 수 있었다.

> ![virus_before](https://user-images.githubusercontent.com/58473522/84213172-e8a69a80-aafa-11ea-8d2f-dd81f0adf3ec.png)<br>
> virus에 관한 사전의 텍스트를 이용한 바이러스 이미지의 wordcloud 구현 예시

위 사진에서 볼 수 있듯이 모든 virus 단어가 viru로 묶여버리는 현상이 발생한다.

이에 대해 원 코드 작성자가 미리 preprocessing을 하는 등의 방식으로 해결책을 제시했지만, 
긴 글의 경우 수많은 단어들을 전처리하기에 무리가 있어 적용하기 쉽지 않은 해결책이다.
<br><br>

우리는 이 이슈를 해결할 수 있을지 의논하였고([issue#2][issue]), 코드를 면밀히 분석해보고 해결해 보기로 하였다.

우선 이 현상이 발생하는 이유를 살펴본 결과 텍스트에 s가 삭제되서는 안되는 단어가 실수등으로 인해 s가 삭제되어 존재하는 경우
(예를 들자면 virus가 viru로 타이핑된 경우)에, `tokenization` 모듈의 `process_tokens` 함수 내부에서 
그 단어 하나로 인해 원래의 모든 단어들이 잘못된 단어로 묶여버리는 매커니즘을 가지고 있기 때문임을 파악했다.

따라서 잘못된 단어가 단어 목록에 들어가 있을때 그 단어가 영어 사전에 등재되어 있는 정상적인 단어인지 체크하는 과정이 단어들을 하나의 frequency로 
묶는 절차 전에 선행되어야 한다고 판단하였고 이 과정을 구현하기 위해 스펠링을 체크해주는 패키지인 [pyenchant][pyenchant] 패키지를 활용하기로 하였다. 
이 역시 오픈소스프로젝트로 진행되고 있는 패키지이며 크게 무겁지 않아 시간적인 측면에서 우려되던 점도 해결 될 수 있었다. 우리는 단지 단어의 존재 여부만 
체크하면 되므로 pyenchant 패키지에서 Dict 모듈만을 사용하였다.

```
from enchant import Dict
eng_d = Dict("en_US")
```

Dict 모듈의 매개변수로 `en_US`를 넘겨주게 되면 영어 단어를 체크해주는 사전 객체가 생성된다.

```
if key.endswith('s') and not key.endswith("ss"):
    key_singular = key[:-1]
    if eng_d.check(key_singular):
```

여기에서 key는 우리가 처리하고자 하는 텍스트가 단어들로 처리된 리스트의 요소들이며, 1~2번째 줄에서 's'로 끝나는 경우에 `key_singular` 변수에 
's'를 제거한 단어 형태로 값을 저장하는 것을 볼 수 있다. 이제 이 변수가 다음 단계로 넘어가기 전에 정상적인 영어 단어인지 체크하기 위해 사전 객체를 
활용하여 `eng_d.check(key_singular)`값이 true가 되는 경우에만 다음 단계를 진행하도록 처리하였다.

이렇게 수정된 `tokenization` 모듈을 사용하는 word cloud 패키지는 이제 plural issue가 발생하지 않으며, 잘못된 단어가 처리되지 않으므로 더욱 
정확한 단어의 빈도수를 가지고 결과물을 만들어 내게 되었다.

> ![virus](https://user-images.githubusercontent.com/58473522/84213216-0a078680-aafb-11ea-9147-0ad94d884155.png)<br>
> Plural Issue 해결 후 이미지. viru같은 잘못된 단어는 처리하지 않도록 작업하였다.



[Plural_Issue_page]: https://github.com/amueller/word_cloud/issues/542
[issue]: https://github.com/20-1-SKKU-OSS/2020-1-OSS-5/issues/2
[pyenchant]: https://github.com/pyenchant/pyenchant
