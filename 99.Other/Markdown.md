
参考文档 http://wowubuntu.com/markdown/
    无论是不是程序员，学会写markdown，就可以专注于内容，而不是格式


宗旨
=============
	Markdown 的目标是实现「易读易写」。

	可读性，无论如何，都是最重要的。
	一份使用 Markdown 格式撰写的文件应该可以直接以纯文本发布，并且看起来不会像是由许多标签或是格式指令所构成。
	总之， Markdown 的语法全由一些符号所组成，这些符号经过精挑细选，其作用一目了然。



兼容 HTML
=============
	Markdown 不是想要取代 HTML，也不是要使得 HTML 文档更容易书写。而是允许内嵌 HTML 编码。
	Markdown 的理念是，能让文档更容易读、写和随意改。Markdown 的格式语法只涵盖纯文本可以涵盖的范围。

	不在 Markdown 涵盖范围之内的标签，都可以直接在文档里面用 HTML 撰写。
	不需要额外标注这是 HTML 或是 Markdown；只要直接加标签就可以了。

	要制约的只有一些 HTML 区块元素――比如 <div>、<table>、<pre>、<p> 等标签，
	必须在前后加上空行与其它内容区隔开，还要求它们的开始标签与结尾标签不能用制表符或空格来缩进。
	Markdown 的生成器有足够智能，不会在 HTML 区块标签外加上不必要的 <p> 标签。

	请注意，在 HTML 区块标签间的 Markdown 格式语法将不会被处理。
	比如，你在 HTML 区块内使用 Markdown 样式的*强调*会没有效果。

	HTML 的区段（行内）标签如 <span>、<cite>、<del> 可以在 Markdown 的段落、列表或是标题里随意使用。
	依照个人习惯，甚至可以不用 Markdown 格式，而直接采用 HTML 标签来格式化。
	与处在 HTML 区块标签间不同，Markdown 语法在 HTML 区段标签间是有效的。




语法
=============

### 1. 标题
Markdown提供了两种方式(Setext 和 Atx)来显示标题。

Setext方式:

	标题1
	=================

	标题2
	-----------------

Atx方式:

	# 标题1
	## 标题2
	###### 标题6

注意： 标题2的写法会自动加横线。



### 2. 换行

	在文字的末尾使用两个或两个以上的空格来表示换行。



### 3. 引用
行首使用>加上一个空格表示引用段落，内部可以嵌套多个引用。
可以在每行的最前面加上 “>”，也可以只在整个段落的第一行最前面加上 “>”。
引用段落里面的换行，还得使用 Markdown 的行末加两个空格。

	> 这是一个引用，
	> 这里木有换行，
	> 在这里换行了。
	> > 内部嵌套



### 4. 列表
无序列表使用*、+或-后面加上空格来表示。
有序列表使用数字加英文句号加空格表示。

	* Item 1
	* Item 2
	* Item 3

	+ Item 1
	+ Item 2
	+ Item 3

	- Item 1
	- Item 2
	- Item 3

	1. Item 1
	2. Item 2
	3. Item 3


使用列表的一些注意事项
如果在单一列表项中包含了多个段落，为了保证渲染正常，*与段落首字母之间必须保留四个空格

*    段落一

     小段一
*    段落二

     小段二


另外，如果在列表中加入了区块引用，区域引用标记符也需要缩进4个空格

* 段落一
    > 区块标记一
* 段落二
    > 区块标记二


### 5. 代码区域
行内代码使用反斜杠`括起来表示。
代码段落则是在每行文字前加4个空格或者1个缩进符表示,此段落必须在前后加上空行与其它内容区隔开。

行内的如 `Something`
段落的如:

	echo 'Something'



### 6. 强调
Markdown使用 * 或 _ 表示强调，显示效果为斜体和加粗。

	单星号 = *斜体*
	单下划线 = _斜体_
	双星号 = **加粗**
	双下划线 = __加粗__
	三星号 = ***这是斜体加粗的文字***
	双波浪线 = ~~这是加删除线的文字~~
	方框 =  -[显示方框]-
	双等号 = ==高亮==    (原版Markdown标准中不存在，但在其大部分衍生标准中被添加)



### 7. 链接
Markdown支持两种风格的链接：Inline和Reference。

	Inline：
	以中括号标记显示的链接文本，后面紧跟用小括号包围的链接。
	如果链接有title属性，则在链接中使用空格加双引号引起"title属性"。
	如：  [链接文字](链接地址 "可选的title")

	Reference：
	一般应用于多个不同位置使用相同链接。通常分为两个部分，调用部分为[链接文本][ref]；
	定义部分可以出现在文本中的其他位置，格式为[ref]: http://some/link/address (可选的标题)。
	注：ref中不区分大小写，这名称可以自定义。

这是一个 [Inline 示例](http://db.tt/ORtPX1Y3 "可选的title")。
这是一个 [Reference 示例][ref1]。
[ref1]:http://db.tt/ORtPX1Y3 "可选的title2"

注：Markdown本身语法不支持链接在新页面中打开，部分网站可能特殊处理过才行。
如果想要在新页面中打开的话可以用html语言的a标签代替。
如：<a href="https://www.jianshu.com/u/1f5ac0cf6a8b" target="_blank">简书</a>


### 8. 图片
图片的使用方法基本上和链接类似，只是在中括号前加叹号。
语法： ![图片alt](图片地址 ''图片title'')
注：Markdown不能设置图片大小，如果必须设置则应使用HTML标记`<img>`。

	Inline示例：![替代文本](/assets/images/jian.jpg "可选的title")
	Reference示例：![替代文本][pic]
	[pic]: /assets/images/ship.jpg "可选的title2"
	HTML示例：<img src="/assets/images/jian.jpg" alt="替代文本" title="标题文本" width="200" />



### 9. 自动链接
使用尖括号，可以为输入的URL或者邮箱自动创建链接。

	如： <test@domain.com>、<http://db.tt/ORtPX1Y3>



### 10. 分隔线
在一行中使用三个或三个以上的 * 、 - 或 _ 可以添加分隔线，其中可以有空白，但是不能有其他字符。

	***
	---
	_  _  _



### 11. 转义字符
Markdown中的转义字符为\，可以转义的有：

	\\ 反斜杠
	\` 反引号
	\* 星号
	\_ 下划线
	\{\} 大括号
	\[\] 中括号
	\(\) 小括号
	\# 井号
	\+ 加号
	\- 减号
	\. 英文句号
	\! 感叹号


### 12. 表格
语法：

	表头|表头|表头
	---|:--:|---:
	内容|内容|内容
	内容|内容|内容


第二行分割表头和内容。
- 有一个就行，为了对齐，多加了几个
文字默认居左
-两边加：表示文字居中
-右边加：表示文字居右
注：原生的语法两边都要用 | 包起来。此处省略


### 13. 代码
语法：
单行代码：代码之间分别用一个反引号包起来

	`代码内容`

代码块：代码之间分别用三个反引号包起来，且两边的反引号单独占一行
要表示具体某种语言，可以在三个点后面加上语言名字
```
  代码...
  代码...
  代码...
```

```javascript
var i = 0;

```


### 14. 流程图

	```flow
	st=>start: 开始
	op=>operation: My Operation
	cond=>condition: Yes or No?
	e=>end
	st->op->cond
	cond(yes)->e
	cond(no)->op
	&```

	上面的“ ```flow ”表示流程图开始，而“ &``` ”表示结束
	“ => ”用来表示定义变量,如上的 st 就表示开始节点，e表示结束节点
	“ -> ”表示流程走向