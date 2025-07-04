var config = {
    type: Phaser.AUTO,
    parent:'game-container',
    width: 800,
    height: 600,
    physics: {
        default: 'arcade',
        arcade: {
            gravity: { y: 300 },
            debug: false
        }
    },
    scene: {
        preload: preload,
        create: create,
        update: update
    },
    plugins: {
        scene: [{
            key: 'rexVirtualJoystick',
            plugin: rexvirtualjoystickplugin,
            mapping: 'joystick'
        }]
    },
};

let player;
let stars;
let bombs;
let platforms;
let cursors;
let score = 0;
let gameOver = false;
let scoreText;

let game = new Phaser.Game(config);

function preload ()
{
    this.load.image('sky', '/static/phaser/sky.png');
    this.load.image('ground', '/static/phaser/platform.png');
    this.load.image('star', '/static/phaser/star.png');
    this.load.image('bomb', '/static/phaser/bomb.png');
    this.load.spritesheet('dude', '/static/phaser/dude.png', { frameWidth: 32, frameHeight: 48 });
}

function create ()
{
    //  A simple background for our game
    this.add.image(400, 300, 'sky');

    //  The platforms group contains the ground and the 2 ledges we can jump on
    platforms = this.physics.add.staticGroup();

    //  Here we create the ground.
    //  Scale it to fit the width of the game (the original sprite is 400x32 in size)
    platforms.create(400, 568, 'ground').setScale(2).refreshBody();

    //  Now let's create some ledges
    platforms.create(600, 400, 'ground');
    platforms.create(50, 250, 'ground');
    platforms.create(750, 220, 'ground');

    // The player and its settings
    player = this.physics.add.sprite(100, 450, 'dude');

    //  Player physics properties. Give the little guy a slight bounce.
    player.setBounce(0.2);
    player.setCollideWorldBounds(true);

    //  Our player animations, turning, walking left and walking right.
    this.anims.create({
        key: 'left',
        frames: this.anims.generateFrameNumbers('dude', { start: 0, end: 3 }),
        frameRate: 10,
        repeat: -1
    });

    this.anims.create({
        key: 'turn',
        frames: [ { key: 'dude', frame: 4 } ],
        frameRate: 20
    });

    this.anims.create({
        key: 'right',
        frames: this.anims.generateFrameNumbers('dude', { start: 5, end: 8 }),
        frameRate: 10,
        repeat: -1
    });

    //  Input Events
    cursors = this.input.keyboard.createCursorKeys();

    // Détection mobile (iPad, iPhone, Android)
    const isMobile = this.sys.game.device.os.android || this.sys.game.device.os.iOS;

    if (isMobile) {
        this.joyStick = this.joystick.add(this, {
            x: 100,
            y: 500,
            radius: 50,
            base: this.add.circle(0, 0, 50, 0x888888),
            thumb: this.add.circle(0, 0, 25, 0xcccccc),
        });

        this.joyStickCursors = this.joyStick.createCursorKeys();
    }

    //  Some stars to collect, 12 in total, evenly spaced 70 pixels apart along the x axis
    stars = this.physics.add.group({
        key: 'star',
        repeat: 11,
        setXY: { x: 12, y: 0, stepX: 70 }
    });

    stars.children.iterate(function (child) {

        //  Give each star a slightly different bounce
        child.setBounceY(Phaser.Math.FloatBetween(0.4, 0.8));

    });

    bombs = this.physics.add.group();

    //  The score
    scoreText = this.add.text(16, 16, 'score: 0', { fontSize: '32px', fill: '#000' });

    //  Collide the player and the stars with the platforms
    this.physics.add.collider(player, platforms);
    this.physics.add.collider(stars, platforms);
    this.physics.add.collider(bombs, platforms);

    //  Checks to see if the player overlaps with any of the stars, if he does call the collectStar function
    this.physics.add.overlap(player, stars, collectStar, null, this);

    this.physics.add.collider(player, bombs, hitBomb, null, this);
}

function update ()
{
    const speed = 160;

    if (gameOver)
    {
        return;
    }

    // Initialisation des vitesses
    player.setVelocityX(0);

    // Détection mobile : joystick actif
    const isUsingJoystick = typeof joyStickCursors !== 'undefined';

    const left = isUsingJoystick ? joyStickCursors.left.isDown : cursors.left.isDown;
    const right = isUsingJoystick ? joyStickCursors.right.isDown : cursors.right.isDown;
    const up = isUsingJoystick ? joyStickCursors.up.isDown : cursors.up.isDown;

    if (left) {
        player.setVelocityX(-speed);
        player.anims.play('left', true);
    }
    else if (right) {
        player.setVelocityX(speed);
        player.anims.play('right', true);
    }
    else {
        player.anims.play('turn');
    }

    if (up && player.body.touching.down) {
        player.setVelocityY(-330);
    }
}

function collectStar (player, star)
{
    star.disableBody(true, true);

    //  Add and update the score
    score += 10;
    scoreText.setText('Score: ' + score);

    if (stars.countActive(true) === 0)
    {
        //  A new batch of stars to collect
        stars.children.iterate(function (child) {

            child.enableBody(true, child.x, 0, true, true);

        });

        let x = (player.x < 400) ? Phaser.Math.Between(400, 800) : Phaser.Math.Between(0, 400);

        let bomb = bombs.create(x, 16, 'bomb');
        bomb.setBounce(1);
        bomb.setCollideWorldBounds(true);
        bomb.setVelocity(Phaser.Math.Between(-200, 200), 20);
        bomb.allowGravity = false;

    }
}

function hitBomb (player, bomb)
{
    this.physics.pause();

    player.setTint(0xff0000);

    player.anims.play('turn');

    gameOver = true;
    scoreText.setText('Game Over! Final Score: ' + score);
    this.input.keyboard.on('keydown-R', function (event) {
        if (gameOver) {
            location.reload(); // Reload the game on pressing 'R'
        }
    });
    this.add.text(200, 300, 'Press CTR+R to Restart', { fontSize: '32px', fill: '#fff' });
}