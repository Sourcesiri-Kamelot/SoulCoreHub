const puppeteer = require('puppeteer');

describe('Landing Page', () => {
  let browser;
  let page;

  beforeAll(async () => {
    browser = await puppeteer.launch();
    page = await browser.newPage();
    await page.goto('http://localhost:8000');
  });

  afterAll(async () => {
    await browser.close();
  });

  test('Header navigation links are visible', async () => {
    const navLinks = await page.$$eval('nav ul li a', links => links.map(link => link.textContent));
    expect(navLinks).toEqual(['Home', 'Features', 'Testimonials', 'Contact']);
  });

  test('Hero section is visible', async () => {
    const heroHeading = await page.$eval('.hero h1', heading => heading.textContent);
    expect(heroHeading).toBe('Welcome to SoulcoreHub');
  });

  test('Features section is visible', async () => {
    const featuresHeading = await page.$eval('.features h2', heading => heading.textContent);
    expect(featuresHeading).toBe('Features');
  });

  test('Testimonials section is visible', async () => {
    const testimonialsHeading = await page.$eval('.testimonials h2', heading => heading.textContent);
    expect(testimonialsHeading).toBe('What Our Users Say');
  });

  test('Contact section is visible', async () => {
    const contactHeading = await page.$eval('.contact h2', heading => heading.textContent);
    expect(contactHeading).toBe('Get in Touch');
  });
});
