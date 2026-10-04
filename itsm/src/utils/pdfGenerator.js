import { Text } from '@react-pdf/renderer';
import MarkdownIt from 'markdown-it';

const styles = {
  page: {
    flexDirection: 'column',
    backgroundColor: '#ffffff',
    padding: 30,
  },
  title: {
    fontSize: 18,
    marginBottom: 15,
    color: '#1c1c1c',
  },
  content: {
    fontSize: 10,
    lineHeight: 1.5,
    color: '#1c1c1c',
  },
  h1: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 10,
    color: '#1c1c1c',
  },
  h2: {
    fontSize: 15,
    fontWeight: 'bold',
    marginBottom: 8,
    color: '#1c1c1c',
  },
  h3: {
    fontSize: 12,
    fontWeight: 'bold',
    marginBottom: 6,
    color: '#1c1c1c',
  },
  bold: {
    fontWeight: 'bold',
  },
  italic: {
    fontStyle: 'italic',
  },
  code: {
    fontFamily: 'Courier',
    backgroundColor: '#f0f0f0',
    padding: 1,
    fontSize: 9,
  },
  codeBlock: {
    fontFamily: 'Courier',
    backgroundColor: '#f0f0f0',
    padding: 8,
    marginBottom: 8,
    fontSize: 9,
  },
  listItem: {
    marginLeft: 15,
    marginBottom: 3,
  },
  paragraph: {
    marginBottom: 6,
  },
};

export const parseMarkdownToPDF = (markdown) => {
  const md = new MarkdownIt();
  const tokens = md.parse(markdown);

  const renderToken = (token) => {
    switch (token.type) {
      case 'heading_open':
        const level = parseInt(token.tag.slice(1));
        return { type: 'heading_open', level };

      case 'heading_close':
        return { type: 'heading_close' };

      case 'paragraph_open':
        return { type: 'paragraph_open' };

      case 'paragraph_close':
        return { type: 'paragraph_close' };

      case 'inline':
        return token.children ? token.children.map(renderToken).flat() : [];

      case 'strong_open':
        return { type: 'strong_open' };

      case 'strong_close':
        return { type: 'strong_close' };

      case 'em_open':
        return { type: 'em_open' };

      case 'em_close':
        return { type: 'em_close' };

      case 'code_inline':
        return { type: 'code_inline', content: token.content };

      case 'code_block':
        return { type: 'code_block', content: token.content };

      case 'bullet_list_open':
        return { type: 'bullet_list_open' };

      case 'bullet_list_close':
        return { type: 'bullet_list_close' };

      case 'list_item_open':
        return { type: 'list_item_open' };

      case 'list_item_close':
        return { type: 'list_item_close' };

      case 'ordered_list_open':
        return { type: 'ordered_list_open' };

      case 'ordered_list_close':
        return { type: 'ordered_list_close' };

      case 'text':
        return { type: 'text', content: token.content };

      case 'softbreak':
        return { type: 'softbreak' };

      case 'hardbreak':
        return { type: 'hardbreak' };

      case 'link_open':
        return { type: 'link_open', href: token.attrGet('href') };

      case 'link_close':
        return { type: 'link_close' };

      default:
        return [];
    }
  };

  const elements = tokens.map(renderToken).flat();

  const renderElements = (elements) => {
    const result = [];
    let currentText = [];
    let inBold = false;
    let inItalic = false;
    let inCode = false;
    let inLink = false;
    let currentLink = null;
    let currentHeadingLevel = null;
    let inParagraph = false;
    let inList = false;
    let inListItem = false;
    let listType = null;
    let listItemNumber = 0;

    for (let i = 0; i < elements.length; i++) {
      const el = elements[i];

      switch (el.type) {
        case 'heading_open':
          currentHeadingLevel = el.level;
          break;

        case 'heading_close':
          if (currentText.length > 0) {
            const headingStyle = currentHeadingLevel === 1 ? styles.h1 :
                                currentHeadingLevel === 2 ? styles.h2 : styles.h3;
            result.push(<Text key={`h-${i}`} style={headingStyle}>{currentText}</Text>);
            currentText = [];
          }
          currentHeadingLevel = null;
          break;

        case 'paragraph_open':
          inParagraph = true;
          break;

        case 'paragraph_close':
          if (currentText.length > 0) {
            result.push(<Text key={`p-${i}`} style={styles.paragraph}>{currentText}</Text>);
            currentText = [];
          }
          inParagraph = false;
          break;

        case 'bullet_list_open':
          inList = true;
          listType = 'bullet';
          break;

        case 'ordered_list_open':
          inList = true;
          listType = 'ordered';
          listItemNumber = 0;
          break;

        case 'bullet_list_close':
        case 'ordered_list_close':
          inList = false;
          listType = null;
          break;

        case 'list_item_open':
          inListItem = true;
          if (listType === 'ordered') {
            listItemNumber++;
          }
          break;

        case 'list_item_close':
          if (currentText.length > 0) {
            const prefix = listType === 'bullet' ? '• ' : `${listItemNumber}. `;
            result.push(
              <Text key={`li-${i}`} style={styles.listItem}>
                {prefix}{currentText}
              </Text>
            );
            currentText = [];
          }
          inListItem = false;
          break;

        case 'strong_open':
          inBold = true;
          break;

        case 'strong_close':
          inBold = false;
          break;

        case 'em_open':
          inItalic = true;
          break;

        case 'em_close':
          inItalic = false;
          break;

        case 'code_inline':
          currentText.push(<Text key={`code-${i}`} style={styles.code}>{el.content}</Text>);
          break;

        case 'code_block':
          result.push(
            <Text key={`codeblock-${i}`} style={styles.codeBlock}>
              {el.content}
            </Text>
          );
          break;

        case 'link_open':
          inLink = true;
          currentLink = el.href;
          break;

        case 'link_close':
          inLink = false;
          currentLink = null;
          break;

        case 'text':
          let textElement = el.content;
          if (inBold) {
            textElement = <Text key={`text-${i}`} style={styles.bold}>{textElement}</Text>;
          }
          if (inItalic) {
            textElement = <Text key={`text-${i}`} style={styles.italic}>{textElement}</Text>;
          }
          if (inLink) {
            textElement = <Text key={`text-${i}`} style={{ color: '#0066cc', textDecoration: 'underline' }}>{textElement}</Text>;
          }
          currentText.push(textElement);
          break;

        case 'softbreak':
          currentText.push(' ');
          break;

        case 'hardbreak':
          currentText.push('\n');
          break;
      }
    }

    // Add any remaining text
    if (currentText.length > 0) {
      result.push(<Text key="final" style={styles.paragraph}>{currentText}</Text>);
    }

    return result;
  };

  return renderElements(elements);
};

export default styles;
