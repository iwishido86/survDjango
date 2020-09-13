(function () {
  var questionIndex = 0;
  var lastQuestionIndex = 11;
  var score = {}
  var elemWrapper = $('.question .contents');
  var typeIndex = [
    'ISTJ',
    'ISTP',
    'ESTP',
    'ESTJ',

    'ISFJ',
    'ISFP',
    'ESFP',
    'INFJ',

    'INFP',
    'INTP',
    'ENTP',
    'ESFJ',

    'ENFP',
    'ENFJ',
    'INTJ',
    'ENTJ',
  ];
  var checkMyType = function (score) {
    var result = ''
    result += score['E'] > score['I'] ? 'E' : 'I'
    result += score['S'] > score['N'] ? 'S' : 'N'
    result += score['T'] > score['F'] ? 'T' : 'F'
    result += score['J'] > score['P'] ? 'J' : 'P'

    return result;
  };
  var handleBtnClick = function ($this, value) {
    questionIndex += 1;

    if (score[value]) {
      score[value] += 1
    } else {
      score[value] = 1
    }

    resultType = checkMyType(score)
    let index = typeIndex.findIndex((type) => type === resultType)
    console.log('handleBtnClick', value, questionIndex, resultType, index, score)

    $this.addClass('selected');
    if (questionIndex > lastQuestionIndex) {
      $('.loading-panel').css({ display: 'block' });
      setTimeout(function() {
        window.location.replace(`/result?result_code=${index}`);
      }, 100);
    } else {
      setTimeout(function() {
        renderQuestion(questionIndex);
      }, 350);
    }
  };

  /**
   * index 인자값으로 질문데이터를 가져오고, 렌더링 후 애니메이션을 초기화합니다(animate.css)
   * @param {number} index
   */
  var renderQuestion = function (index) {
    var renderData = getQuestionData(index);
    var str = '<div class="icon question-answers" style="--animate-delay: 0.1s; --animate-duration: 1s"></div>';
    str += '  <div class="rounding-box question-box question-answers" style="--animate-delay: 0.1s; --animate-duration: 1s">';
    str += '    <div class="top"><div class="center"></div></div>';
    str += '    <div class="body">';
    str += '      <div class="inner-contents">';
    str += '        <div class="q">Q' + (index + 1) + '</div>';
    str += '        <h1>' + renderData.question + '</h1>';
    str += '      </div>';
    str += '    </div>';
    str += '    <div class="bottom"><div class="center"></div></div>';
    str += '  </div>';
    str += '<div class="answer-list btn-area">';
    for (var i = 0; i < renderData.answers.length; i++) {
      str += '  <div class="btn question-answers' + (renderData.smallFont ? ' smallFont' : '') + '" style="--animate-delay: 0.2s; --animate-duration: 1s" data-answer-value="' + renderData.answers[i].value + '"><span>' + renderData.answers[i].text + '</span></div>';
    }
    str += '</div>';

    elemWrapper.html(str);

    const elements = document.querySelectorAll('.question-answers');
    elements.forEach((element) => {
        element.classList.add('animate__animated', 'animate__fadeInUp');
    });

    $('.page-info span').text(index + 1);
    $('.answer-list .btn').on('click', function () {
      var $this = $(this);
      var value = $this.attr('data-answer-value');
      handleBtnClick($this, value);
    });
  }

  renderQuestion(questionIndex);

})()
